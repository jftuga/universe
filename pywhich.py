#!/usr/bin/env python3

r"""
pywhich.py
-John Taylor
May-7-2020

Iterate through the PATH environment variable to search for an executable given as cmd-line argument.
"""

import os
import os.path
import platform
import sys
import concurrent.futures

VERSION="1.2.5"

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

def search(order:int, dname:str, pgm:str) -> list:
    """search for all programs starting with pgm, 
       for 'less', this could return 'less.exe', 'less.ps1', 'lessecho.exe', 'lesskey.exe'

       Args:
        order: the order in the path in which a program appears

        dname: the directory name to search for

        pgm: the program name to search for
    """
    results = []
    if not os.path.exists(dname):
        #print("Error: path not found:", dname)
        return

    all_files = os.listdir(dname)
    n=len(pgm)
    for f in all_files:
        match = False
        if f.lower() == pgm:
            found = os.path.join(dname,f)
            if os.path.isfile(found):
                match = found
                #print(found)
                results.append((order,found))
        orig = f
        f_ext = os.path.splitext(f)[1]
        f_ext = f_ext[1:]
        f = f[:n]
        if f == pgm:
            if f_ext in all_ext:
                found = os.path.join(dname,orig)
                if match != found:
                    if os.path.isfile(found):
                        #print(found)
                        results.append((order,found))
    return results

def unqiue(path_list:list) -> list:
    uniq = []
    for p in path_list:
        if p not in uniq:
            uniq.append(p)
        else:
            print(f"WARNING: '{p}' appears multiple times in PATH", file=sys.stderr)

    return uniq

def main():
    if len(sys.argv) != 2:
        usage()
        return
    pgm = sys.argv[1]
    pgm = pgm.lower()
    all_paths = os.environ['PATH']
    if "Windows" == platform.system():
        all_paths = ".;" + all_paths
    path_list = all_paths.split(os.pathsep)
    path_list = unqiue(path_list)
    
    i = 0
    ordered = {}
    for p in path_list:
        ordered[p] = i
        i+=1

    ordered_results = []
    with concurrent.futures.ThreadPoolExecutor(len(path_list)) as executor:
        result = {executor.submit(search, ordered[path], path, pgm): path for path in path_list}
        for future in concurrent.futures.as_completed(result):
            if future.done():
                all_pgms = future.result()
                if all_pgms and len(all_pgms):
                    for pgm in all_pgms:
                        ordered_results.append(pgm)

    # ensure results are displayed by path order
    ordered_results.sort(key = lambda x: x[0])
    for pgm in ordered_results:
        print(pgm[1])

if "__main__" == __name__:
    main()
