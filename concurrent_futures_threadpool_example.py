#!/usr/bin/env python3

# shows how to use concurrent.futures threads and print its results

import concurrent.futures, threading, random

def example_func(a1: int,a2: int ,x: int) -> int:
	print("\tname:", threading.current_thread().name)
	print("\t\targs:", a1,a2,x)
	return a1* a2 * x

def main():
    max_workers=4
    my_list = [x*x for x in range(1,11)]
    arg1 = random.randint(1,10)
    arg2 = random.randint(11,20)
    with concurrent.futures.ThreadPoolExecutor(max_workers,thread_name_prefix="myprefix") as executor:
        result = {executor.submit(example_func,arg1,arg2,x): x for x in my_list}
        for future in concurrent.futures.as_completed(result):
            if future.done():
                print("result:", future.result())

if "__main__" == __name__:
	main()
