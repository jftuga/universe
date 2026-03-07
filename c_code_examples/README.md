# c_code_examples

## Summary

This is a collection of **teaching and reference snippets** written circa 2001. Viewed through that lens -- pre-C99 widely adopted, personal learning exercises -- they accomplish their goal: demonstrating specific C APIs and concepts in compact, runnable programs. The breadth of topics covered is good, spanning sorting algorithms, binary search, function pointers, System V IPC, `mmap`, binary file I/O, structs, and dynamic memory management.

However, there are real bugs (off-by-one in `strrev.c`, the `fwrite.c` comma typo, missing null terminators in `cookedload.c`, undefined behavior in `comma.c` and `ascii.c`), missing includes, and the mmap pointer check is broken on any 64-bit system. Several files have buffer overflow potential. For production code this would be unacceptable; for personal learning examples from 2001, it is roughly on par for the era.

**Grade: C+**

If the `strrev.c` off-by-one, `cookedload.c` missing null terminators, and `fwrite.c` comma typo were fixed, and the missing `<string.h>` includes added, this would be a solid B.

---

## What Works Well

- **Good topic coverage.** The collection covers a solid range of C fundamentals: sorting algorithms, binary search, `bsearch(3)`, `qsort(3)`, function pointers/callbacks, System V IPC (message queues, shared memory), `mmap`, `fwrite`/`fread`, structs, dynamic memory, and file I/O. For 2001-era teaching/reference examples, the breadth is respectable.
- **Consistent patterns.** Most files follow a similar structure: comment header, includes, functions, main. Argument checking is present in nearly every program.
- **Memory cleanup is attempted.** `bsearchString.c`, `nameage1.c`, `nameage2.c`, and `names.c` all free allocated memory -- many example programs from this era don't bother.
- **Incremental complexity.** The `nameage1.c` to `nameage2.c` progression (fixed array to fully dynamic `realloc`) and `mmap_malloc_test1` to `test2` to `test3` show intentional pedagogical layering.
- **Good use of stdlib.** Proper use of `bsearch`, `qsort`, `strtok`, `sscanf`, `mmap`, `shmget`/`shmat`, etc.

---

## Bugs and Correctness Issues

| File | Issue |
|------|-------|
| `ascii.c:6` | Undefined behavior: `i++` inside `printf` argument while `i` is also used in the format -- the order of evaluation of function arguments is unspecified. |
| `comma.c:10` | `y = ++y` is undefined behavior (modifying `y` twice between sequence points). The whole file is a trick-question puzzle, but the UB makes it non-portable. |
| `atoi.c:11` | Missing `#include <string.h>` for `strlen`. Will compile with implicit declaration on old compilers but is technically wrong. |
| `bsearchString.c:13` | Missing `#include <string.h>` for `strcmp`/`strcpy`/`strlen`. |
| `msgsnd.c:38` | Missing `#include <string.h>` for `strcpy`. |
| `strrev.c:20` | Off-by-one: `malloc(local_strlen(s) * sizeof(char))` -- needs `+1` for the null terminator. The `rev[r] = '\0'` on line 29 writes one byte past the allocation. |
| `fwrite.c:18` | `{ 22.11, 33.22, 44.33, 55.44, 66.55, 77.66, 88.77, 99,88 }` -- the last entry is `99` and `88` as two separate elements (comma operator), not `99.88`. This array has 9 initializers for conceptually 8 slots. |
| `mmap_malloc_test1.c:53`, `test2:57`, `test3:108` | `(int) v < 0` to check mmap failure is wrong on 64-bit systems. Should compare against `MAP_FAILED`. |
| `mmap_malloc_test2.c:44` | `atol` returns `long`, assigned to `int fsize`. Also `O_CREAT` without a mode argument is UB (the permission bits are garbage). |
| `names.c:21` | Classic `while(!feof(stdin))` bug -- will process the last entry twice. |
| `names.c:19` | Operator precedence: `BUFFSIZE+1 * sizeof(char)` evaluates as `BUFFSIZE + (1 * sizeof(char))` due to `*` binding tighter than `+`. Needs parentheses: `(BUFFSIZE+1) * sizeof(char)`. |
| `cookedload.c:40-41` | Strings read via `fread` are never null-terminated. The allocated buffers have room (`c_len+1`) but the terminator is never written. |
| `callback.c:48` | Off-by-one: `type > MAX_EVENT` should be `type >= MAX_EVENT` (valid indices are 0..2, MAX_EVENT is 3). |
| `small_shm_load.c:15` | `#define BUFFER_SIZE 256 * 1048576` -- needs parentheses. As-is, any expression like `BUFFER_SIZE + x` will be wrong. Also allocates 256 MB unconditionally on the heap. |
| `octal.c`, `mmap_malloc_test3.c` | `reverse()` and `Oct2Dec()` are duplicated verbatim across files. Violates DRY, though understandable for standalone examples. |
| `nameage.h` | Declares `compareName`/`compareAge` but the implementations in `nameage1.c` and `nameage2.c` have different struct definitions -- the header's prototypes use `const void*` and are essentially unused. This header adds nothing. |

---

## Style and Practice Issues

- **No `#include <string.h>`** in several files that use `strlen`, `strcmp`, `strcpy` -- relying on implicit declarations (legal in C89 but a source of bugs).
- **`sizeof` format specifier** -- `sizeof` returns `size_t`, but `%d` is used everywhere (`sizeof.c`, `nameage1.c`, `nameage2.c`). Should use `%zu` (C99+) or cast.
- **Casting `malloc` return** -- Not needed in C (and arguably harmful as it can mask a missing `#include <stdlib.h>`). Every `malloc` call is cast. Acceptable in 2001 C89 style, but worth noting.
- **Magic numbers** -- Hard-coded array sizes (`200` in `merge.c`, `MAXPERSON` = 6, etc.) without runtime validation in most cases.
- **Variable naming** -- Heavy use of `loop`, `ptr`, `v`, `fp` everywhere. Functional but not descriptive.
- **`return fprintf(stderr, ...)` as an error-exit idiom** -- clever but misleading. `fprintf` returns the number of characters written, not a meaningful error code. The program exits with an arbitrary positive value.

---

## Security Concerns

- `sprintf(fname, ...)` in `umask_test.c` -- no bounds checking (though the 128-byte buffer is adequate for octal numbers up to 512).
- `strcpy(message.mtext, argv[1])` in `msgsnd.c:38` -- classic buffer overflow if `argv[1]` exceeds 256 bytes.
- `scanf("%s\n", line)` in `names.c` -- unbounded read, potential overflow.
- `urlExtract.c` -- the backward-scanning pointer loop (`for(ptr--; *ptr != ' '; ptr--)`) can scan past the beginning of the buffer if there is no space before the URL at position 0. The `ptr == &buffer[0]` check mitigates this partially, but it is fragile.

---

## File Descriptions

| File | Description |
|------|-------------|
| `ascii.c` | Prints all 255 ASCII characters alongside their decimal values. |
| `atoi.c` | Hand-rolled `atoi` implementation that converts a string to an integer, supporting negative numbers. |
| `BinarySearch.c` | Binary search over a sorted array of strings, with the search term provided on the command line. |
| `bitwise.c` | Demonstrates bitwise operators by computing bits-per-byte and printing powers of two via shift operations. |
| `bsearchInt.c` | Shows how to use the standard library `bsearch(3)` function to search for an integer in a sorted array. |
| `bsearchString.c` | Shows how to use the standard library `bsearch(3)` function to search for a string in a sorted array of strings. |
| `callback.c` | Demonstrates function pointers and a callback dispatch table, randomly invoking registered event handlers. |
| `comma.c` | Puzzle/trick program exercising the C comma operator and ternary expressions. |
| `cookedload.c` | Reads a binary data file (produced by `rawimport.c`) directly into dynamically allocated structs. |
| `fwrite.c` | Demonstrates `fwrite`/`fread` by writing an array of floats to a binary file and reading it back. |
| `InsertionSort.c` | Insertion sort algorithm applied to a small hard-coded array of integers. |
| `itoa.c` | Hand-rolled `itoa` implementation that converts an unsigned integer to its string representation. |
| `merge.c` | Merge sort implementation using a double-buffering technique, with verbose progress output for tutorial purposes. |
| `mmap_malloc_test1.c` | Demonstrates `mmap` and `malloc_stats` using a pre-existing 8 MB file, writing to every other byte. |
| `mmap_malloc_test2.c` | Extends test1 by creating the mmap file from scratch via `ftruncate`, with file name and size from the command line. |
| `mmap_malloc_test3.c` | Extends test2 by adding `fork` to show that mmap'd memory is visible across parent and child processes. Also includes octal conversion and string reversal helpers. |
| `msg_queue/msgsnd.c` | Creates a System V IPC message queue and sends a user-provided message into it. |
| `msg_queue/msgrcv.c` | Retrieves a message from a System V IPC message queue by queue ID, then removes the queue. |
| `nameage.h` | Header declaring comparison function prototypes used by `nameage1.c` and `nameage2.c`. |
| `nameage1.c` | Reads name/age pairs from a file, sorts them by name and by age using `qsort` with a fixed-size array of struct pointers. |
| `nameage2.c` | Same as `nameage1.c` but fully dynamic -- uses `realloc` to grow the array, removing the hard-coded size limit. |
| `names.c` | Reads names from stdin into a dynamically allocated array (via `malloc`/`realloc`) and prints them in reverse order. |
| `octal.c` | Prints all 512 decimal-to-octal pairs for umask values and converts an octal command-line argument to decimal. |
| `pi.c` | Computes and prints the value of pi using `4 * atan(1)`. |
| `rawimport.c` | Parses a pipe-delimited text file of stock data, builds dynamic structs, and writes them out as a binary file for `cookedload.c`. |
| `shared_mem/small_shm_load.c` | Loads the contents of a file into a System V shared memory segment and writes the segment ID to a file. |
| `shared_mem/small_shm_get.c` | Attaches to an existing shared memory segment (by ID from a file) and dumps its contents to an output file. |
| `sizeof.c` | Prints the byte size of each primitive C data type on the current machine. |
| `strrev.c` | Hand-rolled `strlen` and in-place string reversal implementations. |
| `structures.h` | Shared header defining the `stock_data` struct and `BUFFSIZE` constant used by `rawimport.c` and `cookedload.c`. |
| `umask_test.c` | Creates 512 files with every possible Unix permission mode, demonstrating `umask`, `open`, and octal formatting. |
| `urlExtract.c` | Scans gzip-compressed Usenet article files in a directory, extracting URLs by searching for `://` patterns. |
| `usleep.c` | Sleeps for a specified number of microseconds given on the command line. |
| `zeropad.c` | Demonstrates printf zero-padding format specifiers for integers. |

---

## 25-Year Retrospective: What Aged Well and What Didn't

This code was written around 2001, targeting C89/C90 on 32-bit Linux. A quarter century later, C has evolved through C99, C11, C17, and C23. The systems programming landscape has shifted dramatically. Here is what still holds up, what has been superseded, and what has become irrelevant.

### Still Applicable in 2026

- **Core algorithms.** The sorting and searching implementations (`BinarySearch.c`, `InsertionSort.c`, `merge.c`) teach the same fundamentals they did in 2001. These algorithms haven't changed and never will.
- **`qsort` and `bsearch`.**  Both remain the standard C library sort and search functions. The comparator-with-void-pointer pattern in `bsearchInt.c`, `bsearchString.c`, `nameage1.c`, and `nameage2.c` is still how you use them today.
- **Function pointers and callbacks.** The dispatch table pattern in `callback.c` remains a core C idiom. This is still how event systems, plugin architectures, and vtable-style polymorphism work in C codebases.
- **`mmap`.** Memory-mapped I/O (`mmap_malloc_test1-3.c`) is arguably more relevant now than in 2001 -- it underpins modern database engines, file-backed allocators, and zero-copy I/O patterns.
- **`fork` and shared memory visibility.** The demonstration in `mmap_malloc_test3.c` that mmap'd regions survive `fork` is still an important systems programming concept.
- **Binary file I/O with `fread`/`fwrite`.** The `rawimport.c`/`cookedload.c` pair demonstrates serialization fundamentals that remain relevant, even if you'd typically use a proper serialization format today.
- **`printf` formatting.** Zero-padding (`zeropad.c`), octal output (`octal.c`), and format specifiers in general work identically today.
- **Dynamic memory with `malloc`/`realloc`.** The progression from fixed arrays to fully dynamic allocation (`nameage1.c` to `nameage2.c`) teaches a lesson that still matters.

### Superseded Idioms

| Old Idiom (seen in this code) | Modern Replacement | Notes |
|------|-------------|-------|
| Implicit function declarations (missing `#include <string.h>`, etc.) | Explicit includes required | C99 removed implicit `int` declarations. Modern compilers emit errors, not warnings. |
| `(int) mmap_result < 0` to detect failure | `if (ptr == MAP_FAILED)` | Casting pointers to `int` was already dubious on 32-bit; on 64-bit systems it silently truncates and the check is broken. `MAP_FAILED` has been the correct check since POSIX.1-2001. |
| `usleep()` | `nanosleep()` or `clock_nanosleep()` | `usleep` was removed from POSIX.1-2008. `nanosleep` provides the same functionality with nanosecond granularity and proper `EINTR` handling. |
| Casting `malloc` return values | No cast needed in C | Was a C++ compatibility habit. In C, `void *` converts implicitly. The cast can mask a missing `#include <stdlib.h>`. |
| `while (!feof(fp))` loop pattern | Check the return value of the read call directly | The `feof` flag is only set *after* a read fails, so the last iteration always processes stale data. The correct pattern is `while (fgets(...) != NULL)` or `while (scanf(...) == 1)`. |
| `sprintf` for string formatting | `snprintf` (available since C99) | `sprintf` has no bounds checking and is a buffer overflow vector. `snprintf` should always be used instead. |
| `strcpy` / `strcat` | `strncpy` / `strncat`, or better: `snprintf` or `strlcpy` (BSD/POSIX) | Unbounded copies are a classic source of buffer overflows. Modern code should always use length-bounded alternatives. |
| `atoi` / `atol` for number parsing | `strtol` / `strtoul` | `atoi` has no error detection -- it returns 0 for both "0" and "not a number". `strtol` reports errors via `errno` and an end pointer. |
| `return fprintf(stderr, ...)` as error exit | `fprintf(stderr, ...); return EXIT_FAILURE;` or `exit(EXIT_FAILURE)` | `fprintf` returns the character count written, not a meaningful exit code. Using `EXIT_FAILURE` (defined as 1) gives callers a predictable status. |
| CVS `$Id$` and `$Log$` keywords | Git (or any modern VCS) | CVS keyword expansion in source files was standard practice in 2001. Git does not expand keywords by default, and commit history lives in the repository, not in file headers. |
| `#define SIZE 8192*1024` (unparenthesized macros) | `#define SIZE (8192*1024)` or `enum { SIZE = 8192*1024 };` or `static const int SIZE = 8192*1024;` | Unparenthesized macros are a textual substitution hazard. C99+ `enum` constants or `static const` variables avoid this entirely. |
| `scanf("%s", buf)` for string input | `fgets` + `sscanf`, or `scanf("%255s", buf)` with width limit | Unbounded `%s` reads are buffer overflows waiting to happen. |

### Largely Obsolete

- **System V IPC message queues** (`msgsnd.c`, `msgrcv.c`). While the API still exists in the kernel, it has been almost entirely replaced by POSIX message queues (`mq_open`, `mq_send`, `mq_receive`), Unix domain sockets, or higher-level messaging systems. System V message queues have awkward semantics, poor tooling, and kernel-limited resource caps. New code should not use them.
- **System V shared memory** (`small_shm_load.c`, `small_shm_get.c`). Similarly superseded by POSIX shared memory (`shm_open` + `mmap`), which integrates cleanly with the filesystem namespace and `mmap`. The System V `shmget`/`shmat` interface is clunky by comparison and persists mainly for legacy compatibility.
- **Hand-rolling `atoi` and `itoa`** (`atoi.c`, `itoa.c`). Useful as learning exercises, but in practice `strtol`/`strtoul` and `snprintf` have completely replaced the need for custom implementations.
- **Hand-rolling `strrev`** (`strrev.c`). String reversal is a classic interview/teaching exercise but has essentially no real-world use case in C. If needed, it is a one-liner with pointer swaps -- no allocation required.
- **Usenet-specific tooling** (`urlExtract.c`). The zlib-based Usenet article parser is a product of its time. Usenet itself is a niche protocol in 2026, and URL extraction from text would today be done with a regex library or a higher-level language entirely.
- **`malloc_stats()`** (`mmap_malloc_test1-3.c`). This is a glibc extension, not portable, and modern memory analysis uses tools like Valgrind, AddressSanitizer, or `jemalloc`/`tcmalloc` introspection APIs.

### What You'd Do Differently Today

If rewriting these examples for a modern audience:

- **Target C17 or C23** as the baseline standard.
- **Use `bool` from `<stdbool.h>`** (or the C23 built-in `bool`) instead of `int` flags.
- **Use `size_t`** for sizes and lengths, and `%zu` in printf format strings.
- **Use `static_assert`** (C11+) where compile-time invariants matter.
- **Use `errno` and `strerror`** consistently for error reporting instead of ad-hoc messages.
- **Use POSIX IPC** (`shm_open`, `mq_open`) instead of System V equivalents.
- **Use `getopt` or `getopt_long`** for command-line parsing instead of raw `argc`/`argv` checks.
- **Compile with `-Wall -Wextra -Werror -pedantic`** -- most of the bugs in this collection would have been caught at compile time.
