#!/usr/bin/env python3

# pydu2.py
# -John Taylor
# Sep-9-2005
# revamp on Sep-10-2015

# displays recursive directory disk usage, plus totals

import os, sys, locale
from os.path import join, getsize

def safe_print(data):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

# convert 112233.4455 into 112,233.45
def fmt(n,precision=2):
	tmp = "%." + "%s" % (precision) + "f"
	return locale.format(tmp, n, grouping=True)

def main():
	if 1 == len(sys.argv):
		parameter = "."
	else:
		parameter = sys.argv[1]

	total = 0
	dir_total = 0
	file_count = 0
	dir_count = 0
	err_count = 0
	for root, dirs, files in os.walk( parameter ):
		dir_total = 0
		dir_count += 1
		current = 0
		for name in files:
			fullname = join(root,name)
			try:
				current += getsize(fullname)
				file_count += 1
			except:
				safe_print("Error: unable to read: %s" % fullname)
				err_count += 1
		total += current
		dir_total += current

		# directory size in kilobytes
		safe_print("%s\t%s" % (fmt(round(dir_total/1024.0,0),0), root))

	locale.setlocale(locale.LC_ALL, '')
	print()
	print("%s files" % ( fmt(file_count,0) ))
	print("%s directories" % ( fmt(dir_count,0) ))
	if err_count:
		print("%s read errors" % ( fmt(err_count,0) ))

	print()
	print("%s bytes" % ( fmt(total,0) ))
	if total > 1126:
		print("%s kilobytes" % ( fmt(total / 1024.0 )))
	if total > 1153433:
		print("%s megabytes" % ( fmt(total / 1024 ** 2 )))
	if total > 1181116006:
		print("%s gigabytes" % ( fmt(total / 1024.0 ** 3)))
	print()

if "__main__" == __name__:
	main()
