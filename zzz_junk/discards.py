#!/Users/john/opt/bin/python3
import time, sys

fname="stats.txt"

def usage():
	print()
	print()
	print("ssh admin@172.22.3.71")
	print("show int Gi0/10 counters errors | in Gi0/10")
	print()
	print()

def main():
	
	if len(sys.argv) != 2:
		return usage()
	now = int( sys.argv[1] )

	if now < 16000:
		print()
		print("ERROR")
		print("value should be > 16000")
		print()
		return

	tmp = open(fname).read().splitlines()
	last = len(tmp) - 1
	old = int (tmp[last-1])
	old_time = tmp[last]
	now_time = time.strftime("%c")

	print()
	print( old_time, "=>", old )
	print( now_time, "=>", now, "=>", now - old )
	print()

	fp = open(fname,"a")
	fp.write("%s\n" % (now))
	fp.write("%s\n" % (now_time))
	fp.close()


main()
