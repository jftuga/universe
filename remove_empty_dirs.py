
# remove_empty_dirs.py
# -John Taylor

# recursively remove folders that do not contain any files
# TODO: improve --dryrun to be more accurate
# TODO: --keep does not retain the date in all situations, not sure why

import argparse
import os
import os.path
import sys
import time

pgm_version = "1.03"
pgm_date = "Feb-6-2018 8:28"

# a list of directories that could not be removed
STUCK = []

# dry run
DRY = {}

###########################################################################

def convert_to_date(t:float) -> str:
	"""When given a time in floating point format, return a time in human readable format

	Args:
		t: a floating point time, such as: 1517922516.0907083

	Returns:
		a readable date format, such as: 2018-02-06 08:08:36
	"""
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

###########################################################################

def scan_and_remove(root_dir:str,dryrun:bool,keep:bool,single:str) -> int:
	"""Recursively remove empty directories

	Args:
		root_dir: the top-level directory to remove

		dryrun: if True, do not actually remove but just notify what would actually be removed

		keep: if True, retain the date modified timestamp of the parent directory

		single: a file name that is allowed to be deleted as well as the directory it self
		       useful for files such as Thumbs.db

	Returns:
		The number of directories removed
	""" 
	global DRY

	count=0
	for root, dirs, files in os.walk( root_dir,topdown=False ):
		parent = False
		if 1 == len(files) and single == files[0]:
			try:
				if keep:
					parent = os.path.dirname(root)
					statinfo = os.stat( parent )

				single_full_path = os.path.join(root,files[0])
				print("removing single file:", single_full_path)
				os.remove(single_full_path)
				files.clear()
			except PermissionError as err:
				print(err)
				continue

		if not len(files) and not len(dirs):
			if root in DRY:
				continue
			if root.find("DfsrPrivate") > 0:
				continue
			root = os.path.abspath(root)
			count += 1

			try:
				if not dryrun and not keep:
					print("removing directory:", root)
					os.rmdir(root)
				elif not dryrun and keep:
					if not parent:
						parent = os.path.dirname(root)
						statinfo = os.stat( parent )
					modify = statinfo.st_mtime
					print("removing directory:", root)
					os.rmdir(root)
					os.utime(parent,(float(0),float(modify)))
				else:
					DRY[root] = 1
			except PermissionError as err:
				print(err)
				STUCK.append(root)

	return count

###########################################################################

def main():
	global STUCK

	parser = argparse.ArgumentParser(description="recursively remove folders that do not contain any files", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname", help="root level directory")
	parser.add_argument("-d", "--dryrun", help="list directories to be removed, but do not actually remove them", action="store_true")
	parser.add_argument("-k", "--keep", help="keep last modifed time of parent directory the same", action="store_true")
	parser.add_argument("-s", "--single", help="still remove if this one file exists. Useful for Thumbs.db", nargs="?" )

	args = parser.parse_args()
	root_dir = args.dname

	if not os.path.isdir( root_dir ):
		print()
		print("Not a directory: %s" % (root_dir))
		print()
		return


	cycles = 1
	count = 1
	total = 0

	while count:
		print()
		print("Scan cycle:", cycles)
		print("=" * 20)
		count = scan_and_remove(root_dir,args.dryrun,args.keep,args.single)
		total += count
		print()
		if count:
			cycles += 1

	"""
	# remove the root dir given on cmd line, if empty
	if os.path.exists(root_dir):
		remaining = os.listdir(root_dir)
		if not len(remaining):
			try:
				print("removing directory:", root)
				print(root_dir)
				os.rmdir(root_dir)
				total += 1
			except PermissionError as err:
				print(err)
				STUCK.append(root_dir)
	"""

	print()
	print("===")
	print("Total # of scan cycles:", cycles)
	print("Total # of directories removed:", total)
	print("===")
	if len(STUCK):
		print("Directories that could not be removed:")
		for d in STUCK:
			print("   ", d)
		print("===")
	print()

###########################################################################

if "__main__" == __name__:
	main()

