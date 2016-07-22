#!/usr/bin/env python3

# pydu2.py
# -John Taylor
# Sep-9-2005
# revamp on Sep-10-2015, Nov-15-2015, Jul-22-2016

# displays recursive directory disk usage, plus totals

import os, sys, locale, argparse
from os.path import join, getsize, isdir, splitext
from collections import defaultdict

pgm_version = "1.05"
pgm_date = "Jul-22-2016 10:33"



#############################################################################

def safe_print(data,isError=False):
    dest = sys.stdout if not isError else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest )

#############################################################################

# convert 112233.4455 into 112,233.45
def fmt(n,precision=2):
	tmp = "%." + "%s" % (precision) + "f"
	return locale.format(tmp, n, grouping=True)

#############################################################################

def get_disk_usage(parameter=".",want_ext=False,verbose=True,status=False):

	extensions = defaultdict(int)
	longest_ext = ""
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
			if want_ext:
				tmp = os.path.splitext(name)[1][1:].lower()
				extensions[tmp] += 1
				if len(tmp) > len(longest_ext): longest_ext=tmp
			fullname = join(root,name)
			try:
				current += getsize(fullname)
				file_count += 1
			except:
				safe_print("Error: unable to read: %s" % fullname, isError=True)
				err_count += 1
		total += current
		dir_total += current

		# directory size in kilobytes
		if verbose: safe_print("%s\t%s" % (fmt(round(dir_total/1024.0,0),0), root))
		if status:
			if not (dir_count % 100):
				print("Directories processed:", dir_count,file=sys.stderr)

	locale.setlocale(locale.LC_ALL, '')
	print()
	print("%s files" % ( fmt(file_count,0) ))
	print("%s directories" % ( fmt(dir_count,0) ))
	if err_count:
		print("%s read errors" % ( fmt(err_count,0) ))

	print()
	print("%s bytes" % ( fmt(total,0) ))
	# comparison values are about 90.909% of kilo,mega,giga, and terabyte
	if total > 1126:
		print("%s kilobytes" % ( fmt(total / 1024.0 )))
	if total > 1153433:
		print("%s megabytes" % ( fmt(total / 1024 ** 2 )))
	if total > 1181116006:
		print("%s gigabytes" % ( fmt(total / 1024.0 ** 3)))
	if total > 1209462790144:
		print("%s terabytes" % ( fmt(total / 1024.0 ** 4)))
	if total > 1238489897107456:
		print("%s petabytes" % ( fmt(total / 1024.0 ** 5)))
		
	print()

	if want_ext:
		t=0
		width = len(longest_ext)+2
		for e in sorted(extensions, key=extensions.get, reverse=True):
			spc = width - len(e)
			print("%s%s%s" % (e," "*spc,extensions[e]))
		print()
		
#############################################################################

def main():
	parser = argparse.ArgumentParser(description="Display recursive directory disk usage, plus totals", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname", help="directory name", nargs="?", default=".")
	parser.add_argument("-e", "--ext", help="summarize file extensions", action="store_true")
	parser.add_argument("-q", "--quiet", help="don't display individual directories", action="store_true")
	parser.add_argument("-s", "--status", help="send processing status to STDERR", action="store_true")
	args = parser.parse_args()

	verbose = False if args.quiet else True

	if isdir(args.dname):
		try:
			get_disk_usage(args.dname,args.ext,verbose,args.status)
		except KeyboardInterrupt:
			safe_print("", isError=True)
			safe_print("", isError=True)
			safe_print("You pressed Ctrl+C", isError=True)
			safe_print("", isError=True)
			return 1
	else:
		safe_print("", isError=True)
		safe_print("Error: command-line parameter is not a directory: %s" % args.dname, isError=True)
		safe_print("", isError=True)
		return 1

	return 0

#############################################################################

if "__main__" == __name__:
	sys.exit( main() )

