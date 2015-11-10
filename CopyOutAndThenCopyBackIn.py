#!/usr/bin/env python3

""" 
CopyOutAndThenCopyBackIn.py
-John Taylor
Nov-10-2015

fix NTFS perms by copying files from network share to local drive and then back

Make sure there are no thumbs.db files first, with these two commands:
dir /s/b/ah thumbs.db | mawk "{print 'attrib -r -h -s ~'$0'~'}" | tr ~ \042 | cmd
dir /s/b thumbs.db | mawk "{print 'del ~'$0'~'}" | tr ~ \042 | cmd

"""

import os, os.path, shutil, sys, time

# rewt is the location of the original files, dest is a temporary location
REWT="Q\\Department1\\Testing\\Eval"
DEST="C:\\temp\\PlaceHolder"

def reCopy(dname,flist):
	dbg = False

	success_copy_count = 0
	for fname in flist:
		# skip all other files except for "Competencies.docx*"
		if fname.find("Competencies.docx") != 0:
			continue
		
		full = os.path.join(dname,fname)
		if dbg: print(full)

		# copy the file to DEST
		if dbg: print("about to copy %s to %s" % (full,DEST))
		try:
			shutil.copy2(full,DEST)
		except:
			print(); print("Error #500"); print("Colud not copy file:",full); print()
			sys.exit(3)
		if dbg: pause = input("I/O operation sucessful, press enter to continue.")


		# delete the same file from dname (which is the source)
		if dbg: print("about to remove file %s" % (full))
		try:
			os.remove(full)
		except:
			print(); print("Error #510"); print("Colud not remove file:",full); print()
			sys.exit(4)
		if dbg: pause = input("I/O operation sucessful, press enter to continue.")


		# copy file from DEST back to dname, eg. it's original location
		newfull = os.path.join(DEST,fname)
		if dbg: print("about to copy %s to %s" % (newfull,dname))
		try:
			shutil.copy2(newfull,dname)
		except:
			print(); print("Error #520"); print("Colud not copy file:",newfull); print()
			sys.exit(5)
		if dbg: pause = input("I/O operation sucessful, press enter to continue.")


		# delete file from DEST, since this is just a temporary location
		if dbg: print("about to remove file %s" % (newfull))
		try:
			os.remove(newfull)
		except:
			print(); print("Error #530"); print("Colud not remove file:",newfull); print()
			sys.exit(6)
		if dbg: pause = input("I/O operation sucessful, press enter to continue.")
		

		success_copy_count += 1

	return success_copy_count

def main():
	parameter = REWT

	if not os.path.exists(REWT):
		print(); print("Error #400"); print("Path not found:", REWT); print()
		sys.exit(1)

	if not os.path.exists(DEST):
		try:
			os.mkdir(DEST)
		except:
			print(); print("Error #410"); print("Path not found:", REWT); print()
			sys.exit(2)

	dir_count = 0
	skip_count = 0
	print()
	success_copy_count = 0
	for root, dirs, files in os.walk( parameter ):
		if len(files):
			print('%02d files, processing folder: "%s"' % (len(files),root))
			current = reCopy(root,files)
			success_copy_count += current
			dir_count += 1
		else:
			print('No files, skipping folder  : "%s"' % (root))
			skip_count += 1

	print()
	print("folders processed :", dir_count)
	print("folders skipped   :", skip_count)
	print("files copied      :", success_copy_count)
	print()
	return 0

if "__main__" == __name__:
	sys.exit(main())

