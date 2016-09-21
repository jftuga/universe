#!/usr/bin/env python3

import sys, socket

def usage():
    print()
    print("Usage: %s [ fname ]" % (sys.argv[0]))
    print("       fname contains host names, one per line")
    print()

def main():
    if len(sys.argv) != 2:
        return usage()
    else:
        fname = sys.argv[1]

    with open(fname) as fp: lines = fp.read().splitlines()
    for hostname in sorted(lines):
        lower_hostname = hostname.lower()
        try:
            if lower_hostname[0].isdigit() and lower_hostname[1].isdigit():
                addr=1
                ip = socket.gethostbyaddr(lower_hostname)
            else:
                addr=0
                ip = socket.gethostbyname(lower_hostname)
        except:
            print("%s\tfailed" % (lower_hostname))
        else:
            if 0 == addr:
                print("%s\t%s" % (lower_hostname,ip))
            else:
                print("%s\t%s" % (lower_hostname,ip[0]))

if "__main__" == __name__:
    main()
