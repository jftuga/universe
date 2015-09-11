
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
            ip = socket.gethostbyname(lower_hostname)
        except:
            ip = "(falied)"
        print("%s\t%s" % (lower_hostname, ip))

main()
