
import sys
import time
import datetime

#################################################################

def usage():
    print()
    print("Usage: %s HR:MM:SS:MS" % (sys.argv[0]))
    print("hour should be given in 24-hr time")
    print("seconds and microseconds are optional")
    print()

#################################################################

def main():
    if 1 == len(sys.argv):
        usage()
        return 1

    slots = sys.argv[1].split(":")

    try:
        hour = int(slots[0])
        minute = int(slots[1])
        second = 0 if 2 == len(slots) else int(slots[2])
        microsecond = 0 if len(slots) <= 3 else int(slots[3])
    except:
        usage()
        return 1


    start = datetime.datetime.today()
    until = start.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    print("start time  :", start)
    print("sleep until :", until)
    if(start >= until):
        print()
        print("Given time is in the past, program aborted.")
        print()
        return 1
    
    cycle = 0.001

    try:
        while 1:
            current = datetime.datetime.today()
            if current >= until:
                print("final time  :", current)
                return 0
            time.sleep(cycle)
    except KeyboardInterrupt:
        print("You pressed Ctrl+C")
        print("final time  :", current)
        return 1

    return 0

#################################################################

if __name__ == '__main__':
    sys.exit(main())
