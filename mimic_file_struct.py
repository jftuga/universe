
# mimic_file_struct.py
# -John Taylor
# Jan-14-2005
# Dec-15-2015 - updated for Python 3

# duplicate a directory & file structure with the exception that all files are zero-length "dummy" files

import os, os.path, sys

if 3 != len( sys.argv ):
	print()
	print("Usage: %s [src dir] [dst dir]" % ( sys.argv[0] ) )
	print()
	sys.exit(1)

SRC=sys.argv[1]
DST=sys.argv[2]

if os.sep != DST[-1]:
	DST = DST + os.sep

fp=None
dir_total=0
file_total=0
i=1
j=0

# Count the number of directories
for root, dirs, files in os.walk( SRC ):
	dir_total += 1
dir_total = float(dir_total)

# Process the directories, and each file in those directories
for root, dirs, files in os.walk( SRC ):
	(drive, tail) = os.path.splitdrive(root)
	target_dir = "%s%s" % ( DST, tail )
	
	# create the directory, if it does not exist
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
		percent = 100 * ( i / dir_total )
		print("[ %4.2f%% ] %s" % ( percent, target_dir), end="" )
		i += 1

	# create a zero length file
	j=0
	for fname in files:
		target_file = r"%s\%s" % (target_dir, fname)
		j = j + 1
		fp = open( target_file, "w")
		fp.close()

	print(" [ %d ]" % ( j ) )
	file_total += j
	
print()
print("%d directories, %d files" % (dir_total, file_total))
print()

