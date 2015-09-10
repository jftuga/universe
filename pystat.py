
# pystat.py
# -John Taylor
# Jul-22-2015

# display metadata of file given on cmd line

import sys, os, os.path, time

def usage():
	print()
	print("Usage:")
	print("%s [ filename ]" % sys.argv[0])
	print()

def convert_to_date(t):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))


def examine_file(fname):
	statinfo = os.stat(fname)
	#print( statinfo )
	print()
	print("name  : %s" % (fname))
	print("size  : {:,}".format(statinfo.st_size))
	print("ctime : %s" % (convert_to_date(statinfo.st_ctime)))
	print("mtime : %s" % (convert_to_date(statinfo.st_mtime)))
	print("atime : %s" % (convert_to_date(statinfo.st_atime)))
	print()

def main():
	if len(sys.argv) != 2:
		return usage()

	fname = sys.argv[1]
	if not os.path.exists(fname):
		print()
		print("File not found: %s" % (fname))
		print()
		return
	examine_file(fname)


main()
