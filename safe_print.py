#!/usr/bin/env python3

# safe_print.py
# -John Taylor

# output print stmts to the screen without have to worry
# about unicode exceptions

import sys

def safe_print(data,isError=False):
    dest = sys.stdout if not isError else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest )

if "__main__" == __name__:
    safe_print("normal message")
    safe_print("error_mesage", True)

