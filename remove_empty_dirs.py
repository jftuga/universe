
# remove_empty_dirs.py
# -John Taylor
# Feb-4-2015
# updated on Oct-31-2015, Nov-18-2015, Jul-29-2017

# recursively remove folders that do not contain any files
# TODO: improve --dryrun to be more accurate

import os, sys, argparse

pgm_version = "1.02"
pgm_date = "Jul-29-2017 16:01"

# a list of directories that could not be removed
STUCK = []

# dry run
DRY = {}

###########################################################################

def scan_and_remove(root_dir:str,dryrun:bool) -> int:
	"""Recursively remove empty directories

	Args:
		root_dir: the top-level directory to remove

		dryrun: if True, do not actually remove but just notify what would actually be removed

	Returns:
		The number of directories removed
	""" 
	global DRY

	count=0
	for root, dirs, files in os.walk( root_dir,topdown=False ):
		if not len(files) and not len(dirs):
			if root in DRY:
				continue
			if root.find("DfsrPrivate") > 0:
				continue
			count += 1
			print(root)
			try:
				if not dryrun: 
					os.rmdir(root)
				else:
					DRY[root] = 1
			except PermissionError as err:
				print(err)
				STUCK.append(root)

	return count

###########################################################################

def main():
	parser = argparse.ArgumentParser(description="recursively remove folders that do not contain any files", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname", help="root level directory")
	parser.add_argument("-d", "--dryrun", help="list directories to be removed, but do not actually remove them", action="store_true")
	args = parser.parse_args()

	root_dir = args.dname

	dryrun = False
	if args.dryrun:
		dryrun = True

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
		count = scan_and_remove(root_dir,dryrun)
		total += count
		print()
		if count:
			cycles += 1

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

