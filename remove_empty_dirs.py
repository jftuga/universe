
# remove_empty_dirs.py
# -John Taylor
# Feb-4-2015
# updated on Oct-31-2015

# recursively remove folders that do not contain any files

import os, sys

STUCK = []


def scan_and_remove(root_dir):
	count=0
	for root, dirs, files in os.walk( root_dir,topdown=False ):
		if not len(files) and not len(dirs):
			if root.find("DfsrPrivate") > 0:
				continue
			count += 1
			print(root)
			try:
				os.rmdir(root)
			except PermissionError as err:
				print(err)
				STUCK.append(root)

	return count


def main():

	if len(sys.argv) != 2:
		print()
		print("Usage:")
		print("%s [ directory name ]" % (sys.argv[0]))
		print()
		return
	else:
		root_dir = sys.argv[1]

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
		count = scan_and_remove(root_dir)
		total += count
		print()
		if count:
			cycles += 1

	print()
	print("===")
	print("Total # of scan cycles:", cycles)
	print("Total # of directories removied:", total)
	print("===")
	if len(STUCK):
		print("Directories that could not be removed:")
		for d in STUCK:
			print("   ", d)
		print("===")
	print()


if "__main__" == __name__:
	main()

