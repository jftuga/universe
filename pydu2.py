#!/usr/bin/env python3

# pydu2.py
# -John Taylor
# Sep-9-2005
# revamp on Sep-10-2015, Nov-15-2015

# displays recursive directory disk usage, plus totals

import os, sys, locale, argparse
from os.path import join, getsize, isdir

pgm_version = "1.00"
pgm_date = "Nov-16-2015 15:24"

#############################################################################

def safe_print(data):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

#############################################################################

# convert 112233.4455 into 112,233.45
def fmt(n,precision=2):
	tmp = "%." + "%s" % (precision) + "f"
	return locale.format(tmp, n, grouping=True)

#############################################################################

def get_disk_usage(parameter=".",verbose=True):
	
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
		if verbose: safe_print("%s\t%s" % (fmt(round(dir_total/1024.0,0),0), root))

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

#############################################################################

def main():
	parser = argparse.ArgumentParser(description="Display recursive directory disk usage, plus totals", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname", help="directory name", nargs="?", default=".")
	parser.add_argument("-q", "--quiet", help="don't display individual directories", action="store_true")
	args = parser.parse_args()

	verbose = False if args.quiet else True
	if isdir(args.dname):
		get_disk_usage(args.dname,verbose)
	else:
		print(); safe_print("Error: command-line parameter is not a directory: %s" % args.dname); print()
		return 1

	return 0

#############################################################################

if "__main__" == __name__:
	sys.exit( main() )
