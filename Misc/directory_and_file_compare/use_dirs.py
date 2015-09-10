
import os, os.path, cPickle, time, sys
from collections import defaultdict,OrderedDict,namedtuple

sys.setrecursionlimit(25000)

if len(sys.argv) <> 3:
	print
	print "Usage:"
	print "%s rewt-dir pkl-file" % (sys.argv[0])
	print
	sys.exit(1)

rewt = sys.argv[1]
pkl_fname = sys.argv[2]

valid_ext = { ".3g2":1, ".bmp":1, ".cue":1, ".exe":1, ".flac":1, ".flv":1, ".gif":1, ".html":1, ".iso":1, ".it":1, ".jpg":1, ".log":1, ".m3u":1, ".m4a":1, ".m4p":1, ".mid":1, ".mod":1, ".mov":1, ".mp3":1, ".mp4":1, ".nfo":1, ".ogg":1, ".pls":1, ".rar":1, ".sfk":1, ".sfv":1, ".txt":1, ".url":1, ".wav":1, ".wma":1, ".xm":1 } 

dir_stack = []
dentry = namedtuple("dentry","ditems dsize")
matrix = defaultdict(dentry)

def process_dir(d):
	artist = "Music"
	album = "Main Directory"
	genre = "Unknown Genre"
	dbg = 2
	slots = d.split("\\")

	# len(slots) == 3 ~ rewt directory
	# len(slots) == 4 ~ main genre directory
	if len(slots) <= 4:
		dont_add = 1
	else:
		dont_add = 0
		genre = slots[3]
		artist = slots[4]
		album = "===".join(slots[5:])

	if 2 == dbg:
		print "-" * 105
	if "%s+++%s+++%s" % (genre,artist,album) in matrix:
		if 2 == dbg: print "duplicate_found: %s+++%s+++%s" % (genre,artist,album)
		album = "Misc-%s" % (slots[3])
		if 2 == dbg: print "changing album to: %s" % (album)

	#############################################################################################################

	if 2 == dbg:
		print "depth  : %d" % len(matrix)
		print "slots  : %d" % len(slots)
		print "direc  :", d
		print "genre  : _%s_" % (genre)
		print "artist : _%s_" % (artist)
		print "album  :", album
		print "-" * 105
	if 3 == dbg:
		print d
	items = 0
	total_size = 0
	file_list = [os.path.join(d, fn) for fn in os.listdir(d)]
	for fname in file_list:
		#print "fn: ", fname
		#full_path = d + os.sep + fname
		#full_path = os.path.join(d, fname)
		#full_path = full_path.encode("utf-8")
		if os.path.isdir(fname):
			# push onto stack
			dir_stack.append(fname)
		elif fname[-4:].lower() in valid_ext:
			# file w/ valid extension
			try:
				fsize = os.path.getsize(fname)
			except WindowsError, e:
				print e
				fsize = 0
			if 2 == dbg: print fname, fsize
			total_size += fsize
			items += 1
	if "%s+++%s+++%s" % (genre,artist,album) in matrix:
		if 2 == dbg: print "2duplicate_found: %s+++%s+++%s" % (genre,artist,album)

	if not dont_add:
		matrix["%s+++%s+++%s" % (genre,artist,album)] = dentry(items, total_size)


	if len(dir_stack):
		process_dir( dir_stack.pop() )



process_dir( rewt )
print len(matrix)
print matrix
# """
pkl_fp = open(pkl_fname, "wb")
cPickle.dump(matrix, pkl_fp, cPickle.HIGHEST_PROTOCOL)
pkl_fp.close()

validate = open(pkl_fname, "rb")
mat2 = cPickle.load(validate)
validate.close()

print "-" * 111
print "final_count: ", len(mat2) - 1
print mat2
print
print "valid? %d " % (mat2 == matrix)
# """
