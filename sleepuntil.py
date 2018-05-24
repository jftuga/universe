
import sys
import time
import datetime

#################################################################

def main():
    slots = sys.argv[1].split(":")

    hour = int(slots[0])
    minute = int(slots[1])
    second = 0 if 2 == len(slots) else int(slots[2])
    microsecond = 0 if 3 == len(slots) else int(slots[3])

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

#################################################################

if __name__ == '__main__':
    main()
