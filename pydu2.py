#!/usr/bin/env python3

# pydu2.py
# -John Taylor

# display directory disk usage in kilobytes, plus totals

import os, sys, locale, argparse, time, statistics
from os.path import join, getsize, isdir, splitext
from collections import defaultdict

pgm_version = "1.20"
pgm_date = "Dec-29-2016 11:22"

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

def display_file_stats(stats_file_sizes):
			print("file statistics (in bytes)")
			print("=" * 26)

			try:
				mean = statistics.mean(stats_file_sizes)
			except:
				print("mean     : N/A")
			else:
				print("mean     : %s" % fmt(mean,0))

			try:
				median = statistics.median(stats_file_sizes)
			except:
				print("median   : N/A")
			else:
				print("median   : %s" % fmt(median,0))

			try:
				mode = statistics.mode(stats_file_sizes)
			except:
				print("mode     : N/A")
			else:
				print("mode     : %s" % fmt(mode,0))

			try:
				stdev = statistics.stdev(stats_file_sizes)
			except:
				print("stdev    : N/A")
			else:
				print("stdev    : %s" % fmt(stdev,0))

#############################################################################

def display_summary(file_count,err_count,dir_count,total,stats,stats_file_sizes):
		print("summary")
		print("=" * 7)

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

		if stats and len(stats_file_sizes):
			display_file_stats(stats_file_sizes)

#############################################################################

def display_extentions(longest_ext,extensions):
		print("file extensions")
		print("=" * 15)
		t=0
		width = len(longest_ext)+2
		for e in sorted(extensions, key=extensions.get, reverse=True):
			spc = width - len(e)
			print("%s%s%s" % (e," "*spc,extensions[e]))
		print()

#############################################################################

def display_status(dir_count,time_begin):
	if not (dir_count % 100):
		print("Directories processed:", dir_count,file=sys.stderr)
		time_begin = time.time()

	# give user more feedback about number of directories processed
	if not (dir_count % 5):
		if ( time.time() - time_begin ) > 0.2:
			print("Directories processed:", dir_count,file=sys.stderr)
			time_begin = time.time()

	return time_begin

#############################################################################

def get_disk_usage(parameter=".",want_ext=False,verbose=True,status=False,skipdot=False,stats=False,bare=False,norecurse=False,verbose_files=False):
	extensions = defaultdict(int)
	longest_ext = ""
	total = 0
	dir_total = 0
	file_count = 0
	dir_count = 0
	err_count = 0
	time_begin = time.time()
	stats_file_sizes = []
	dot_dir = os.sep + "."

	for root, dirs, files in os.walk( parameter ):
		if skipdot and dot_dir in root:
			# skip directories beginning with a '.'
			continue
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
				if stats:
					stats_file_sizes.append(current)
				file_count += 1
			except:
				safe_print("Error: unable to read: %s" % fullname, isError=True)
				err_count += 1
		total += current
		dir_total += current

		# display directory size in kilobytes
		if verbose: safe_print("%s\t%s" % (fmt(round(dir_total/1024.0,0),0), root))
		elif verbose_files: safe_print("%s\t%s\t%s" % (fmt(round(dir_total/1024.0,0),0), len(files), root))

		if status:
			time_begin = display_status(dir_count,time_begin)

		if norecurse: break
	# end of main directory loop

	locale.setlocale(locale.LC_ALL, '')
	
	if not bare: print()
	if want_ext:
		display_extentions(longest_ext,extensions)
	else:
		if not bare: print()	

	if not bare:
		display_summary(file_count,err_count,dir_count,total,stats,stats_file_sizes)

#############################################################################

def main():
	parser = argparse.ArgumentParser(description="Display directory disk usage in kilobytes, plus totals", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname", help="directory name", nargs="?", default=".")
	parser.add_argument("-b", "--bare", help="do not print summary; useful for sorting when used exclusively", action="store_true")
	parser.add_argument("-e", "--ext", help="summarize file extensions", action="store_true")
	parser.add_argument("-q", "--quiet", help="don't display individual directories", action="store_true")
	parser.add_argument("-s", "--status", help="send processing status to STDERR", action="store_true")
	parser.add_argument("-n", "--nodot", help="skip directories starting with '.'", action="store_true")
	parser.add_argument("-N", "--norecurse", help="do not recurse", action="store_true")
	parser.add_argument("-f", "--files", help="also display number of files in each directory", action="store_true")
	parser.add_argument("-S", "--stats", help="display mean, median, mode and stdev file statistics", action="store_true")
	args = parser.parse_args()

	verbose = False if args.quiet else True
	verbose = False if args.files else verbose

	if isdir(args.dname):
		try:
			get_disk_usage(args.dname,args.ext,verbose,args.status,args.nodot,args.stats,args.bare,args.norecurse,args.files)
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

