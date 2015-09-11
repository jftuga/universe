
# safe_print.py
# -John Taylor

# output print stmts to the screen without have to worry
# about unicode exceptions

import sys

def safe_print(data):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )


