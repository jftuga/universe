#!/usr/bin/env python3

r"""
pywhich.py
-John Taylor
May-7-2020

Iterate through the PATH environment variable to search for an executable given as cmd-line argument.
"""

import os
import os.path
import sys
import concurrent.futures

VERSION="1.2.1"

# common Windows executable file extensions
all_ext = ( "bat", "cmd", "com", "cpl", "exe", "inf", "ini", "job", "lnk", "msc", "msi", "msp", "mst", 
    "paf", "pif", "ps1", "py", "reg", "rgs", "scr", "sct", "shb", "shs", "u3p", "rb",
    "vb", "vbe", "vbs", "vbscript", "ws", "wsf", "wsh" )

def usage():
    print()
    print("pywhich, v%s" % (VERSION))
    print("Search for a program that is located in the environment PATH")
    print()
    print("Give program name without any file extension on the cmd-line")
    print("Example: pywhich curl")
    print()

def search(dname:str, pgm:str):
    if not os.path.exists(dname):
        #print("Error: path not found:", dname)
        return

    all_files = os.listdir(dname)
    n=len(pgm)
    for f in all_files:
        match = False
        if f.lower() == pgm:
            found = os.path.join(dname,f)
            match = found
            print(found)
        orig = f
        f_ext = os.path.splitext(f)[1]
        f_ext = f_ext[1:]
        f = f[:n]
        if f == pgm:
            if f_ext in all_ext:
                found = os.path.join(dname,orig)
                if match != found:
                    print(found)


def main():
    if len(sys.argv) != 2:
        usage()
        return
    pgm = sys.argv[1]
    pgm = pgm.lower()
    all_paths = os.environ['PATH']
    all_paths = ".;" + all_paths
    path_list = all_paths.split(";")
    with concurrent.futures.ThreadPoolExecutor(len(path_list)) as executor:
        {executor.submit(search, path, pgm): path for path in path_list}


if "__main__" == __name__:
    main()
 