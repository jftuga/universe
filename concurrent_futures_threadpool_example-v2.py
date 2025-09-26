#!/usr/bin/env python3
r"""
concurrent_futures_threadpool_example-v2.py
-John Taylor
2025-09-26

Disclaimer: The following comments are AI-generated.

A multithreaded program demonstrating concurrent.futures.ThreadPoolExecutor with thread-safe output.
Uses a threading lock to ensure clean, non-interleaved output to STDOUT.

This demo shows the complete lifecycle of concurrent execution:

Timeline of Execution:
1. Creation: executor.submit() creates Future objects immediately, but no computation happens yet
2. Execution: The thread pool runs the functions in the background on separate threads
3. Completion: as_completed() yields futures as they finish, then future.result() retrieves the computed values

Why This Works:
- as_completed() only returns futures that have finished executing completely
- By the time we call future.result(), the computation is already done and the result is ready
- If we called future.result() right after executor.submit(), it would block and wait for completion
- This pattern allows us to process results as soon as they're available, regardless of submission order

Thread-Safe Printing Performance:
The print_lock can range from negligible to significant performance impact:

When Performance Impact is MINIMAL:
- Infrequent printing (occasional progress updates)
- I/O bound tasks (file/network operations dwarf print time)
- Few threads (2-4 threads create minimal contention)
- Print time exceeds lock acquisition time

When Performance Impact is SIGNIFICANT:
- Print-heavy workloads (thousands of prints per second)
- CPU-bound tasks (fast calculations make print locks a bigger % of total time)
- Many threads (20+ threads create serious lock contention)
- Complex string formatting while holding the lock such as heavy f-string processing while holding the lock

Real-World Impact Estimates:
- Light printing (few prints per second): < 1% slowdown
- Moderate printing (dozens per second): 5-15% slowdown
- Heavy printing (hundreds+ per second): 20-50%+ slowdown

Bottom Line:
For most typical applications, the print_lock approach is perfectly fine. The correctness benefit
(clean output) usually outweighs the small performance cost. Only optimize if profiling shows
printing is actually a bottleneck.
"""

import concurrent.futures
import threading
import random
from typing import Union

# Global lock for thread-safe printing
print_lock = threading.Lock()


def thread_safe_print(message: str) -> None:
    """
    Print a message in a thread-safe manner.

    When a thread wants to print, it must first acquire the lock. If another
    thread is currently printing, the requesting thread will wait until the
    lock is released.

    Args:
        message: The message to print to STDOUT.
    """
    with print_lock:
        print(message)


def example_func(a1: int, a2: int, x: int) -> float:
    """
    Perform a mathematical operation and print the calculation details.

    Args:
        a1: First multiplier.
        a2: Second multiplier.
        x: Divisor.

    Returns:
        The result of (a1 * a2) / x.

    Raises:
        ZeroDivisionError: When x is zero.
    """
    thread_safe_print(f"[{threading.current_thread().name}] {a1} * {a2} / {x}")
    return a1 * a2 / x


def main() -> None:
    """
    Main function that demonstrates concurrent execution with clean output.

    Creates random data, executes calculations across multiple threads,
    and handles both successful results and exceptions.
    """
    max_workers = 4
    my_list = [random.randint(0, 5) for _ in range(12)]
    arg1 = random.randint(1, 10)
    arg2 = random.randint(11, 20)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers, thread_name_prefix="myprefix"
    ) as executor:
        # Submit all tasks
        # The dictionary contains:
        # - Keys: Future objects (not yet executed)
        # - Values: The original input values (x from my_list)
        #
        # EXECUTION STARTS HERE: Each executor.submit() call immediately queues the task
        # and starts execution on an available worker thread (if one is free).
        # While the main thread is still submitting more tasks in this loop,
        # the worker threads are already running example_func() in the background.
        future_to_value = {
            executor.submit(example_func, arg1, arg2, x): x for x in my_list
        }

        # Process completed futures
        for future in concurrent.futures.as_completed(future_to_value):
            if future.done():
                exception = future.exception()
                if exception:
                    thread_safe_print(f"[  ERROR   ] {exception}")
                    continue
                thread_safe_print(f"[  result  ] {future.result()}")


if __name__ == "__main__":
    main()
