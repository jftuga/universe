#!/usr/bin/env python3

# pystat.py
# -John Taylor
# Nov-10-2017

# display and/or set metadata of file given on cmd line

import argparse
import os
import os.path
import sys
import time

def convert_to_date(t:float) -> str:
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

def examine_file(fname:str,access:str,modify:str):
	statinfo = os.stat(fname)
	#print(statinfo)

	if modify and access:
		os.utime(fname,(float(access),float(modify)))
		print("%s: access and modify times have been changed." % (fname))
		return

	if modify:
		access = statinfo.st_atime
		os.utime(fname,(float(access),float(modify)))
		print("%s: modify time has been changed." % (fname))
		return

	if access:
		modify = statinfo.st_mtime
		os.utime(fname,(float(access),float(modify)))
		print("%s: access time has been changed." % (fname))
		return

	print()
	print("name  : %s" % (fname))
	print("size  : {:,}".format(statinfo.st_size))
	print("ctime : %s : %s" % (convert_to_date(statinfo.st_ctime),statinfo.st_ctime))
	print("mtime : %s : %s" % (convert_to_date(statinfo.st_mtime),statinfo.st_mtime))
	print("atime : %s : %s" % (convert_to_date(statinfo.st_atime),statinfo.st_atime))


def main():
	parser = argparse.ArgumentParser(description="Get / Set file time stamps")
	parser.add_argument("fname", help="file name", nargs="+")
	parser.add_argument("-a", help="set file access time, fmt: secs.nsecs")
	parser.add_argument("-m", help="set file modification time, fmt: secs.nsecs")
	args = parser.parse_args()

	for fn in args.fname:
		if not os.path.exists(fn):
			print()
			print("File not found: %s" % (fn))
			print()
			return
	
	for fn in args.fname:
		examine_file(fn,args.a,args.m)
	print()


if __name__ == "__main__":
	main()
