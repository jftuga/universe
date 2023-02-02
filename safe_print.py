#!/usr/bin/env python3

# safe_print.py
# -John Taylor

# output print stmts to the screen without have to worry
# about unicode exceptions

import sys
from inspect import getframeinfo

def safe_print(data,isError=False):
    dest = sys.stdout if not isError else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest )

def safe_debug(e: Exception, frame, trace: bool = False):
    if trace:
        filename = getframeinfo(frame).filename
        function = getframeinfo(frame).function
        lineno = getframeinfo(frame).lineno
        safe_print(f"[{filename}:{function}:{lineno}] {e}")
    else:
        safe_print(e)

def example():
    import inspect
    try:
        a = 5 / 0
    except Exception as e:
        safe_debug(e, inspect.currentframe(), trace=True)    

if "__main__" == __name__:
    safe_print("normal message")
    safe_print("error_message", True)

    example()
