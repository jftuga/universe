#!/usr/bin/env python3

"""
dir_compare.py
Compare files in two (or more) directories
-John Taylor

written with Python 3.4.3 on Windows 7
tested on Windows 8.1, OS X 10.10.5 and Ubuntu Linux 14.04

debug reminder: import pdb; pdb.set_trace()

todo 
------
-x to only compare files with a colon-deliemited list of extensions
example: -x .m:.c:.h:.txt
"""

# displayed when running dir_compare.py -h
pgm_version = "4.19"
pgm_date = "Aug-28-2015 11:46"

##########################################################################################################

import sys,platform

def py_version_check():
	min_minor = 3

	msg  = "\n\n"
	msg += "Error."
	msg += "\n\n"
	msg += "You must be running Python 3.%s or newer for this script to operate.\n" % (min_minor)
	msg += "You are running version %s" % (platform.python_version())
	msg +="\n\n"

	major = int(platform.python_version_tuple()[0])
	minor = int(platform.python_version_tuple()[1])

	if major != 3:
		safe_print(msg)
		sys.exit(1)

	if minor < min_minor:
		safe_print(msg)
		sys.exit(1)

# if version is OK, then main() will be executed next
py_version_check()

##########################################################################################################


# makes it easy to copy/paste a cmd line to compare two non-identical (but similar) files
# this value is set by the get_default_cmp_pgm() functions
want_cmp_pgm = True
str_cmp_pgm = None

# skip unimportant files - these will not show up in any output, as they are completely skipped
# these are regular expressions
want_regexpr_skip_filelist = True
regexpr_skip_filelist = ( "~$", "\.swp$","^~\$", "\.tmp$", "Thumbs.db", "\.lnk$", "Destinations-ms$" )
compiled_regexpr_skip_filelist = []

# the above want_regexpr_skip_filelist is only used in print_diff()
# if you want to exclude these files from print_same(), print_exclusive_d1(), print_exclusive_d2()
# then set this to True (the default is False)
want_global_skip_filelist = False

# skip unimportant directories - these will not show up in any output, as they are completely skipped
# these are regular expressions
want_regexpr_skip_dirlist = True
regexpr_skip_dirlist = ( "cache", "recent", "cookies", "\$recycle.bin" )
compiled_regexpr_skip_dirlist = []

# if want_cmp_pgm is true and cmp_min_ratio > 0, then only show the str_cmp_pgm line for files with
# ratios >= cmp_min_ratio
# in other words do not show a str_cmp_pgm for files that are not anywhere similar
# a number closer to 100 means two files are very similar
cmp_min_ratio = 70.00

# if SequenceMatcher takes longer than tis value, abort and then fall through to the next
# quickest comparision method
# this value is in seconds and can be a float
compute_ratio_timeout = 4.25

# skip difference computation for certain file extensions
want_skip_diff_list = True
skip_diff_list = (".pst", ".tmp" )

# some types of files are VERY slow when using the standard difflib ratio() function to compute file similarity
# therefore use the real_quick_ratio() function instead
want_real_quick_diff_list = True
real_quick_diff_list = (".min.css", ".min.js" )

# do not run similarity computation on file greater than this size
# 1 MB = 1 * (1024 * 1024)
# default is 20 MB
want_file_size_diff_limit = True
file_size_diff_limit = 20 * ( 1024 * 1024 )

# verbose: print directory names to STDERR
# controlled by -v cmd line option
# Example: dir_compare.py -r alpha beta > output.log
#          this will display (to the terminal) each directory group as they are being compared 
want_verbose_dir_print = False

# if False, file contents will be compared, not just their metadata
# controlled by -c cmd line option
shallow_cmp = True

# only show files that have the same file size and timestamp
# controlled by -i cmd line option
only_show_same = False

# statistics summary
# controlled by -s cmd line option
count_same_files = 0
count_diff_files = 0
count_unequal_files = 0
count_exclusive_d1 = 0
count_exclusive_d2 = 0
skipped_files = []
skipped_directories = []

# time how long it takes for SequenceMatcher.ratio() to run
# displayed after all files have been compared when using the -S option
elapsed_ratio_time = {}

# output difference to html files
# controlled by -H cmd line option
html_output_dir = None

# Compute a similarity ratio between 2 files
# controlled by -n cmd line option
want_ratio_computation = True

# Output format type
# controlled by -t cmd line option
tab_file = None
ofmt_delim = "\t"
date_time_fmt = "%a %b %d %H:%M:%S %Y"

"""
example csv output:
comparison_value,dname1,dname2,fname,ratio,fsize1,fsize2,fsize_diff,date1,date2,date_diff

all possible comparison values:
samemeta,samemeta_diffdata,idential,different,exclusive_d1,exclusive_d2
identical only occurs with -c (compare contents & metadata)
"""

##########################################################################################################
##########################################################################################################
##########################################################################################################

"""
the Python filecmp implementation is broken
see also: https://bugs.python.org/issue1234674

this modification returns false for a filecmp() when modification times are different
"""

import filecmp, stat

_cache = {}
BUFSIZE = 1024*1024

def DC_cmp(f1, f2, shallow=True):
	global _cache

	#print("FLAG DC_cmp shallow: %s" % (shallow))
	s1 = DC_sig(os.stat(f1))
	s2 = DC_sig(os.stat(f2))
	
	if s1[0] != stat.S_IFREG or s2[0] != stat.S_IFREG:
		#print("FLAG DC_cmp")
		return False
	if shallow: 
		#print("result: %s" % (s1==s2))
		return s1 == s2
	if s1[1] != s2[1]:
		return False

	outcome = _cache.get((f1, f2, s1, s2))
	if outcome is None:
		outcome = DC_do_cmp(f1, f2)
		if len(_cache) > 100:	  # limit the maximum size of the cache
			_cache.clear()
		_cache[f1, f2, s1, s2] = outcome
	return outcome

def DC_sig(st):
	return (stat.S_IFMT(st.st_mode),st.st_size,st.st_mtime)

def DC_do_cmp(f1, f2):
	global BUFSIZE

	bufsize = BUFSIZE
	with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
		while True:
			b1 = fp1.read(bufsize)
			b2 = fp2.read(bufsize)
			if b1 != b2:
				return False
			if not b1:
				return True

def DC_private_cmp(a, b, sh, abs=abs, cmp=DC_cmp):
	#print("FLAG DC_private_cmp")
	try:
		return not abs(DC_cmp(a, b, sh))
	except OSError:
		return 2

"""
therefore: these filecmp functions must be redefined (and overridden) to our own DC_* functions
"""
filecmp.cmp = DC_cmp
filecmp._cmp = DC_private_cmp
filecmp._sig = DC_sig
filecmp._do_cmp = DC_do_cmp

##########################################################################################################

"""
SequenceMatcher in the difflib module contain ratio() and quick_ratio() methods which can take a long time to run with certain input.
One example is two slightly different versions of jquery.min.js.
This subclass adds a timeout to these methods.
The new functionality also has the capability to "fall through" to the next quickest comparison method should a timeout occur.
If a timeout does occur and using a fall through method is not desired, then -1 is returned for the ratio.
See also: https://bugs.python.org/issue24904
"""

import difflib
from timeit import default_timer as _default_timer

def _calculate_ratio(matches, length):
    if length:
        return 2.0 * matches / length
    return 1.0

class DC_SequenceMatcher(difflib.SequenceMatcher):	
	def __init__(self,isjunk=None, a='', b='', autojunk=True, timeout=0, fallthrough=0):
		"""
		Optional arg timeout should be set to the number of seconds to wait
        for ratio() or quick_ratio() to complete.  If a timeout seconds is
        exceeded return -1 for the ratio unless fallthrough is set. This value
        can be a float.

        Optional arg fallthrough should be set to 1 or 2. If ratio() is
        called and fallthrough is set to 1, quick_ratio() will be 
        subsequently called when a timeout occurs. real_quick_ratio()
        will be called if timeout is set to 2 if another timeout
        occurs. If quick_ratio() is initially called and fallthrough
        is set to 1 or 2, real_quick_ratio() will be called when a
        timeout occurs.
		"""
		self.isjunk = isjunk
		self.a = self.b = None
		self.autojunk = autojunk
		self.set_seqs(a, b)
		# number of seconds to wait for ratio() or quick_ratio() to complete
		self.timeout = timeout
		# when ratio() or quick_ratio() times out, fall through to next
        # 1 or 2 comparison methods: quick_ratio() and then real_quick_ratio()
		self.fallthrough = fallthrough
		# used to keep track of a timeout occurence in ratio()
		self.abort_ratio = False

	def find_longest_match(self, alo, ahi, blo, bhi):
		a, b, b2j, isbjunk = self.a, self.b, self.b2j, self.bjunk.__contains__
		besti, bestj, bestsize = alo, blo, 0
		
		j2len = {}
		nothing = []
		start_time = _default_timer()
		for i in range(alo, ahi):
			if self.timeout and (_default_timer() - start_time) > self.timeout:
				self.abort_ratio = True
				return (alo, blo, 0)
			
			j2lenget = j2len.get
			newj2len = {}
			for j in b2j.get(a[i], nothing):
				if j < blo:
					continue
				if j >= bhi:
					break
				k = newj2len[j] = j2lenget(j-1, 0) + 1
				if k > bestsize:
					besti, bestj, bestsize = i-k+1, j-k+1, k
			j2len = newj2len

		while besti > alo and bestj > blo and \
			  not isbjunk(b[bestj-1]) and \
			  a[besti-1] == b[bestj-1]:
			besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
		while besti+bestsize < ahi and bestj+bestsize < bhi and \
			  not isbjunk(b[bestj+bestsize]) and \
			  a[besti+bestsize] == b[bestj+bestsize]:
			bestsize += 1

		while besti > alo and bestj > blo and \
			  isbjunk(b[bestj-1]) and \
			  a[besti-1] == b[bestj-1]:
			besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
		while besti+bestsize < ahi and bestj+bestsize < bhi and \
			  isbjunk(b[bestj+bestsize]) and \
			  a[besti+bestsize] == b[bestj+bestsize]:
			bestsize = bestsize + 1

		return difflib.Match(besti, bestj, bestsize)

	def get_matching_blocks(self):
		if self.matching_blocks is not None:
			return self.matching_blocks
		la, lb = len(self.a), len(self.b)

		queue = [(0, la, 0, lb)]
		matching_blocks = []
		start_time = _default_timer()
		while queue:
			alo, ahi, blo, bhi = queue.pop()
			i, j, k = x = self.find_longest_match(alo, ahi, blo, bhi)
			if self.timeout and (_default_timer() - start_time) > self.timeout:
				self.abort_ratio = True
				return []

			if k:
				matching_blocks.append(x)
				if alo < i and blo < j:
					queue.append((alo, i, blo, j))
				if i+k < ahi and j+k < bhi:
					queue.append((i+k, ahi, j+k, bhi))
		matching_blocks.sort()

		i1 = j1 = k1 = 0
		non_adjacent = []
		for i2, j2, k2 in matching_blocks:
			# Is this block adjacent to i1, j1, k1?
			if i1 + k1 == i2 and j1 + k1 == j2:
				k1 += k2
			else:
				if k1:
					non_adjacent.append((i1, j1, k1))
				i1, j1, k1 = i2, j2, k2
		if k1:
			non_adjacent.append((i1, j1, k1))

		non_adjacent.append( (la, lb, 0) )
		self.matching_blocks = list(map(difflib.Match._make, non_adjacent))
		return self.matching_blocks

	def ratio(self):
		matches = sum(triple[-1] for triple in self.get_matching_blocks())
		if self.abort_ratio:
			if self.fallthrough > 0:
				self.fallthrough -= 1
				return self.quick_ratio()
			else:
				return -1
		return _calculate_ratio(matches, len(self.a) + len(self.b))

##########################################################################################################
##########################################################################################################
##########################################################################################################

import os, os.path, time, re, argparse, shutil, timeit, operator
from datetime import datetime
from itertools import zip_longest

##########################################################################################################

textchars = bytearray([0,7,8,9,10,12,13,27]) + bytearray(range(0x20, 0x100))
textdict = dict(zip_longest(textchars,[''],fillvalue=''))
is_binary_string = lambda data: True if not len(data) else bool(data.translate(textdict))

##########################################################################################################

def get_default_cmp_pgm():
	global str_cmp_pgm

	if "Windows" == platform.system():
		candidates = ( "C:\\Program Files\\WinMerge\\WinMergeU.exe", "C:\\Program Files (x86)\\WinMerge\\WinMergeU.exe", "c:\Program Files\KDiff3\kdiff3.exe", "c:\Program Files (x86)\KDiff3\kdiff3.exe" )
		for c in candidates:
			if os.path.exists(c):
				str_cmp_pgm = c
				break

	elif "Linux" == platform.system():
		candidates = ( "/usr/bin/kdiff3", "/usr/bin/diff" )
		for c in candidates:
			if os.path.exists(c):
				str_cmp_pgm = c
				break
						
	elif "Darwin" == platform.system():
		candidates = ( "/usr/bin/opendiff", "/Applications/kdiff3.app/Contents/MacOS/kdiff3", "/usr/bin/diff" )
		for c in candidates:
			if os.path.exists(c):
				str_cmp_pgm = c
				break

	else:
		candidates = ( "/usr/bin/diff", "/usr/local/bin/diff" )

	# instead of displaying the full path, only display the pgm name if it resides on the OS shell's path
	if str_cmp_pgm:
		base = os.path.basename(str_cmp_pgm)
		if shutil.which(base):
			str_cmp_pgm = base

		if str_cmp_pgm.find(" ") >= 0:
			str_cmp_pgm = '"%s"' % (str_cmp_pgm)

##########################################################################################################

def process_directories(d1,d2,diff_only=False,recurse=False):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories

	abort = False
	if want_regexpr_skip_dirlist and within_regexpr_skip_dirlist(d1): 
		abort = d1
	elif want_regexpr_skip_dirlist and within_regexpr_skip_dirlist(d2): 
		abort = d2

	if abort:
		skipped_directories.append(abort)
		safe_print()
		safe_print("Directory excluded by reg expr skip list: %s" % (abort))
		safe_print()
		return

	if not os.path.exists(d1):
		safe_print()
		safe_print()
		safe_print("Directory path does not exist: %s" % (d1))
		safe_print()
		sys.exit(1)

	if not os.path.exists(d2):
		safe_print()
		safe_print()
		safe_print("Directory path does not exist: %s" % (d2))
		safe_print()
		sys.exit(1)

	if not os.path.isdir(d1):
		safe_print()
		safe_print()
		safe_print("Not a directory: %s" % (d1))
		safe_print()
		sys.exit(1)

	if not os.path.isdir(d2):
		safe_print()
		safe_print()
		safe_print("Not a directory: %s" % (d2))
		safe_print()
		sys.exit(1)

	if d1 == d2:
		safe_print()
		safe_print()
		safe_print("Identical directories given as parameters.")
		safe_print()
		sys.exit(1)

	if want_regexpr_skip_filelist:
		for r in regexpr_skip_filelist:
			compiled_regexpr_skip_filelist.append( re.compile(r,re.I))

	if want_regexpr_skip_dirlist:
		for r in regexpr_skip_dirlist:
			compiled_regexpr_skip_dirlist.append( re.compile(r,re.I))

	meta =  filecmp.dircmp(d1, d2)
	
	dest = sys.stdout
	if recurse:
		for i in range(0,4): safe_print("",outfile=dest)
		safe_print("=" * 135,outfile=dest)
		safe_print("directory 1: %s" % (d1), outfile=dest)
		safe_print("directory 2: %s" % (d2), outfile=dest)
		safe_print("=" * 135, outfile=dest)
		safe_print(outfile=dest)

	if want_verbose_dir_print:
		dest = sys.stderr
	
		for i in range(0,4): safe_print(outfile=dest)
		safe_print("=" * 135,outfile=dest)
		safe_print("directory 1: %s" % (d1), outfile=dest)
		safe_print("directory 2: %s" % (d2), outfile=dest)
		safe_print("=" * 135, outfile=dest)
		safe_print(outfile=dest)

	if diff_only or not only_show_same:
		print_differ(meta,d1,d2)
	
	if not diff_only:
		unequal = print_same(meta,d1,d2)
		if unequal:
			print_unequal( unequal )

		if not only_show_same:
			print_exclusive_d1(meta,d1,d2)
			print_exclusive_d2(meta,d1,d2)

	if recurse:
		for i in range(0,4): safe_print()

##########################################################################################################

def safe_print(data="",outfile=sys.stdout):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=outfile )

##########################################################################################################

def find_common(a0,b0):
	a = a0[::-1]
	b = b0[::-1]

	max=len(a)
	for i in range(0,max):
		if a[0:i] != b[0:i]: break

	for j in range(i,0,-1):
		if a[j] == os.sep and b[j] == os.sep:
			break
	
	tmp = a[:j]
	new_a = tmp[::-1]
	tmp = b[:j]
	new_b = tmp[::-1]

	if(new_a != new_b):
		return os.path.basename(new_a)
	else:
		return new_a

##########################################################################################################

def within_regexpr_skip_filelist(fname):
	# set dbg to a filename fragment (or an entire filename) to debug which files are being skipped
	dbg = False

	for r in compiled_regexpr_skip_filelist:
		match = r.findall(fname)
		if len(match): 
			if dbg: safe_print(":: fname skip positive: %s %s" % (fname, match))
			return True

	if dbg: safe_print(":: fname skip negative: %s %s" % (fname, match))
	return False

##########################################################################################################

def within_regexpr_skip_dirlist(dname):
	for r in compiled_regexpr_skip_dirlist:
		match = r.findall(dname)
		if len(match): return True

	return False

##########################################################################################################

def print_listing(meta,root=True):
	if root:
		quote_left  = '"%s"' % (meta.left)
		quote_right = '"%s"' % (meta.right)
		msg = "%s %s %s" % (os.path.basename(sys.argv[0]),quote_left,quote_right)
		safe_print(msg)

	for key in sorted(meta.subdirs.keys()):
		sub = meta.subdirs[key]
		quote_left  = '"%s"' % (sub.left)
		quote_right = '"%s"' % (sub.right)
		msg = "%s %s %s" % (os.path.basename(sys.argv[0]),quote_left,quote_right)
		safe_print(msg)
		print_listing( filecmp.dircmp(sub.left,sub.right), False )

##########################################################################################################

def recurse_directories(meta, diff_only):
	for key in sorted(meta.subdirs.keys()):
		sub = meta.subdirs[key]
		process_directories( sub.left, sub.right, diff_only=diff_only, recurse=True )
		recurse_directories( filecmp.dircmp(sub.left,sub.right), diff_only )

##########################################################################################################

def print_unequal(unequal):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories
	global want_file_size_diff_limit, file_size_diff_limit, want_skip_diff_list, want_ratio_computation, tab_file

	safe_print()
	safe_print("-" * 135)
	safe_print(" " * 40 + "files contents are unequal, but metatdata is the same")
	safe_print("-" * 135)
	safe_print()

	safe_print("%67s    %10s   %24s" % ("fname", "size", "date"))
	safe_print("%67s    %10s     %24s" % ("="*33, "="*10, "="*24))

	for grp in unequal:
		count_unequal_files += 1
		file1 = grp[0]
		file2 = grp[1]
		a = os.stat(file1)
		b = os.stat(file2)

		tmp=time.localtime(a.st_mtime)
		g = time.asctime(tmp)

		tmp=time.localtime(b.st_mtime)
		h = time.asctime(tmp)

		safe_print("%67s    %10s     %24s" % (make_ellipses(file1,67), a.st_size, g))
		safe_print("%67s    %10s     %24s" % (make_ellipses(file2,67), a.st_size, h))
		if len(unequal) > 1: safe_print("%67s    %10s     %24s" % ("."*33, "."*9,"."*24))
		if tab_file:
			need_ratio = want_ratio_computation
			if want_file_size_diff_limit:
				if os.path.getsize(file1) > file_size_diff_limit or os.path.getsize(file2) > file_size_diff_limit:
					need_ratio = False

			if want_skip_diff_list:
				if file_in_skip_diff_list(file1,file2):
					need_ratio = False
			
			if need_ratio:
				ratio = compute_ratio(file1,file2)
			else:
				ratio = 0.0

			dirname1 = os.path.dirname(file1)
			dirname2 = os.path.dirname(file2)

			basename1 = os.path.basename(file1)
			basename2 = os.path.basename(file2)
			basename = basename1 if basename1 == basename2 else "????"

			save_tab_file("samemeta_diffdata",dirname1,dirname2,basename,ratio,a.st_size,b.st_size,g,h)

	safe_print()
	safe_print()

##########################################################################################################

def print_differ(meta,d1,d2):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories, want_ratio_computation, tab_file

	if not len(meta.diff_files):
		safe_print()
		safe_print("-" * 135)
		safe_print(" " * 40 + "there are no differing files")
		safe_print("-" * 135)
		return

	for i in range(0,6):
		safe_print()
	
	safe_print("-" * 135)
	safe_print(" " * 40 + "files that differ [%s] (star denotes newer or larger file; higher ratio denotes more similarity)" % len(meta.diff_files))
	safe_print("-" * 135)
	safe_print()

	safe_print("%67s    %10s     %10s      %24s    %24s     %6s" % ("fname", "size-1", "size-2", "date-1", "date-2","ratio"))
	safe_print("%67s    %10s     %10s       %24s     %24s    %6s" % ("="*33, "="*10, "="*10, "="*24, "="*24, "="*6))

	cmp_results = []
	files_processed = 0
	for f in sorted(meta.diff_files):
		if want_regexpr_skip_filelist and within_regexpr_skip_filelist(f): 
			skipped_files.append( "%s%s%s" % (d1,os.sep,f) )
			continue
		count_diff_files += 1
		
		file1 = "%s%s%s" % (d1,os.sep,f)
		file2 = "%s%s%s" % (d2,os.sep,f)
		try:
			a = os.stat(file1)
			b = os.stat(file2)

			x=" "
			y=" "
			if a.st_size > b.st_size:
				x="*"
				y=" "
			elif a.st_size < b.st_size:
				x=" "
				y="*"

			j=" "
			k=" "
			if a.st_mtime > b.st_mtime:
				j="*"
				k=" "
			elif a.st_mtime < b.st_mtime:
				j=" "
				k="*"
			
			tmp=time.localtime(a.st_mtime)
			g = time.asctime(tmp)
	
			tmp=time.localtime(b.st_mtime)
			h = time.asctime(tmp)
		except OSError as err:
			dest=sys.stderr
			safe_print("Error #6821 - error while processing file in print_differ()", outfile=dest)
			safe_print(err,outfile=dest)
			safe_print("",outfile=dest)
			continue

		need_ratio = want_ratio_computation
		if want_file_size_diff_limit:
			if os.path.getsize(file1) > file_size_diff_limit or os.path.getsize(file2) > file_size_diff_limit:
				need_ratio = False

		if want_skip_diff_list:
			if file_in_skip_diff_list(file1,file2):
				need_ratio = False
			
		if need_ratio:
			ratio = compute_ratio(file1,file2)
		else:
			ratio = 0.0

		if "-100" == "%d" % (ratio):
			# set to -1 when a ratio() function times out
			ratio = -1
			percent_sign = ""
		else:
			percent_sign="%"

		files_processed += 1
		safe_print("%67s    %10s%s    %10s%s      %24s%s    %24s%s   %4.2f%s" % (make_ellipses(f,67), a.st_size, x, b.st_size, y,  g,j,  h,k, ratio,percent_sign))
		if tab_file:
			save_tab_file("different",d1,d2,f,ratio,a.st_size,b.st_size,g,h)

		if want_cmp_pgm and cmp_min_ratio and str_cmp_pgm:
			if ratio >= cmp_min_ratio - 0.01:
				entry = '%s "%s%s%s" "%s%s%s"' % (str_cmp_pgm,d1,os.sep,f,d2,os.sep,f)
				cmp_results.append(entry)

		if html_output_dir:
			html = difflib.HtmlDiff(tabsize=4,wrapcolumn=65)

			valid_read = True
			try:
				with open(file1,"r") as fp: file1_data = fp.readlines()
				with open(file2,"r") as fp: file2_data = fp.readlines()
			except:
				#print("Unexpected error #7092:", sys.exc_info()[0])
				file1_data = []
				file2_data = []
				valid_read = False

			if not len(file1_data): valid_read = False
			if not len(file2_data): valid_read = False

			if valid_read and not is_binary_string(file1_data[0]) and not is_binary_string(file1_data[len(file1_data)-2]):
				try:
					diff = html.make_file(file1_data,file2_data,"dir 1","dir 2",True)
				except RuntimeError as err :
					dest=sys.stderr
					tmp1 = "%s%s%s" % (d1,os.sep,f)
					tmp2 = "%s%s%s" % (d2,os.sep,f)
					safe_print("Error #5395 - unable to create HTML diff file between:", outfile=dest)
					safe_print("       file1: %s" % (tmp1))
					safe_print("       file2: %s" % (tmp2))
					safe_print(err,outfile=dest)
					safe_print("",outfile=dest)
				else:
					common_name = find_common(file1,file2)
					html_fname = "%s%s%s.html" % (html_output_dir,os.sep,common_name)
					rootdir = os.path.dirname(html_fname)
					#safe_print("html_output_dir: %s    html_fname: %s   rootdir: %s" % (html_output_dir, html_fname,rootdir))
					try:
						os.makedirs(rootdir,mode=0o777,exist_ok=True)
					except OSError as err:
						dest=sys.stderr
						safe_print("Error #4602 - error while creating directory: %s" % (html_output_dir), outfile=dest)
						safe_print(err,outfile=dest)
						safe_print("",outfile=dest)
						continue
					except:
						print("Unexpected error #2183:", sys.exc_info()[0])

					fp = open(html_fname,mode="w")
					fp.write(diff)
					fp.close()
		
	if not files_processed:
		safe_print("%67s" % ("All files were excluded by the file skip list regular expression."))

	if want_cmp_pgm and len(cmp_results):
		safe_print()
		safe_print("-" * 135)
		safe_print(" " * 40 + "command-line file compare (ratio >= %4.2f%%)" % (cmp_min_ratio))
		safe_print("-" * 135)
		safe_print()
		for entry in cmp_results:
			safe_print(entry)

	return files_processed

##########################################################################################################

def print_same(meta,d1,d2):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories, tab_file

	actually_different = []

	if not len(meta.same_files):
		safe_print()
		safe_print("-" * 135)
		safe_print(" " * 40 + "there are no matching files")
		safe_print("-" * 135)
		return

	safe_print()
	safe_print()
	safe_print()
	safe_print()
	safe_print("-" * 135)
	safe_print(" " * 37 + "files that are the same [%s]" % len(meta.same_files))
	safe_print("-" * 135)
	safe_print("%67s    %10s   %24s" % ("fname", "size", "date"))
	safe_print("%67s    %10s     %24s" % ("="*33, "="*10, "="*24))

	for f in sorted(meta.same_files):
		if want_regexpr_skip_filelist and want_global_skip_filelist and within_regexpr_skip_filelist(f): 
			skipped_files.append( "%s%s%s" % (d1,os.sep,f) )
			continue
		count_same_files += 1

		if not shallow_cmp:
			f1 = "%s%s%s" % (d1,os.sep,f)
			f2 = "%s%s%s" % (d2,os.sep,f)
			identical = filecmp.cmp(f1,f2,shallow=False)
			#identical = DC_cmp(f1,f2,shallow=False)
			if not identical:
				actually_different.append( (f1,f2))
				continue

		try:
			a = os.stat("%s%s%s" % (d1,os.sep,f))
			b = os.stat("%s%s%s" % (d2,os.sep,f))

			tmp=time.localtime(b.st_mtime)
			q = time.asctime(tmp)
		except OSError as err:
			dest=sys.stderr
			safe_print("Error #9724 - error while processing file in print_same()", outfile=dest)
			safe_print(err,outfile=dest)
			safe_print("",outfile=dest)
			q = "????"

		safe_print("%67s    %10s     %24s" % (make_ellipses(f,67), a.st_size, q))
		if tab_file:
			comparison_value = "samemeta" if shallow_cmp else "identical"
			save_tab_file(comparison_value,d1,d2,f,100.0,a.st_size,b.st_size,q,q)


	safe_print()
	safe_print()

	return actually_different if len(actually_different) else False

##########################################################################################################

def print_exclusive_d1(meta,d1,d2):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories, tab_file

	if not len(meta.left_only):
		safe_print()
		safe_print("-" * 135)
		safe_print(" " * 30 + "there are no files exclusively in: %s" % (d1))
		safe_print("-" * 135)
		return	

	for i in range(0,4): safe_print(outfile=sys.stdout)
	safe_print("-" * 135)
	safe_print(" " * 30 + "files exclusively in [%s]: %s" % (len(meta.left_only),d1))
	safe_print("-" * 135)
	safe_print("%67s    %10s   %24s" % ("fname", "size", "date"))
	safe_print("%67s    %10s     %24s" % ("="*33, "="*10, "="*24))
	for f in sorted(meta.left_only):
		if want_regexpr_skip_filelist and want_global_skip_filelist and within_regexpr_skip_filelist(f): 
			skipped_files.append( "%s%s%s" % (d1,os.sep,f) )
			continue
		count_exclusive_d1 += 1

		a = os.stat("%s%s%s" % (d1,os.sep,f))
		tmp=time.localtime(a.st_mtime)
		q = time.asctime(tmp)

		safe_print("%67s    %10s     %24s" % (make_ellipses(f,67), a.st_size, q))
		if tab_file:
			save_tab_file("exclusive_d1",d1,"",f,"",a.st_size,"",q,"")
	safe_print()
	safe_print()

##########################################################################################################

def print_exclusive_d2(meta,d1,d2):	
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories, tab_file

	if not len(meta.right_only):
		safe_print()
		safe_print("-" * 135)
		safe_print(" " * 30 + "there are no files exclusively in: %s" % (d2))
		safe_print("-" * 135)
		return	

	for i in range(0,4): safe_print(outfile=sys.stdout)
	safe_print("-" * 135)
	safe_print(" " * 30 + "files exclusively in [%s]: %s" % (len(meta.right_only),d2))
	safe_print("-" * 135)
	safe_print("%67s    %10s   %24s" % ("fname", "size", "date"))
	safe_print("%67s    %10s     %24s" % ("="*33, "="*10, "="*24))
	for f in sorted(meta.right_only):
		if want_regexpr_skip_filelist and want_global_skip_filelist and within_regexpr_skip_filelist(f): 
			skipped_files.append( "%s%s%s" % (d1,os.sep,f) )
			continue
		count_exclusive_d2 += 1

		b = os.stat("%s%s%s" % (d2,os.sep,f))
		tmp=time.localtime(b.st_mtime)
		q = time.asctime(tmp)

		safe_print("%67s    %10s     %24s" % (make_ellipses(f,67), b.st_size, q))
		if tab_file:
			save_tab_file("exclusive_d2","",d2,f,"","",b.st_size,"",q)
	safe_print()
	safe_print()

##########################################################################################################

def make_ellipses(fname, sz):
	w = len(fname)
	if w <= sz:
		return fname

	#segment = floor(sz/2)
	segment = sz // 2
	segment -= 1
	return "%s...%s" % (fname[0:segment],fname[ (w-segment):])

##########################################################################################################

def file_in_skip_diff_list(f1,f2):
	for tmp in skip_diff_list:
		ext = tmp.lower()
		w = len(ext) * -1
		if f1[w:].lower() == ext and f2[w:].lower() == ext:
			return True

	return False

##########################################################################################################

def compute_ratio(file1,file2):
	global elapsed_ratio_time, compute_ratio_timeout

	try:
		with open(file1,"rb") as fp: file1_data = fp.read()
		with open(file2,"rb") as fp: file2_data = fp.read()
	except:
		print("Unexpected error #6739:", sys.exc_info()[0])
		return 0

	s = DC_SequenceMatcher( None, file1_data, file2_data, timeout=compute_ratio_timeout)		
	#safe_print("%s %s" % (file1,file2))
	#safe_print("%s %s" % (is_binary_string(file1_data), is_binary_string(file2_data)))

	if want_real_quick_diff_list:
		for tmp in real_quick_diff_list:
			ext = tmp.lower()
			w = len(ext) * -1
			if file1[w:].lower() == ext and file2[w:].lower() == ext:
				start_time = timeit.default_timer()
				ratio = s.real_quick_ratio()
				elapsed = timeit.default_timer() - start_time
				elapsed_ratio_time[file1] = elapsed
				return ratio * 100.0
				return ratio * 100.0 if ratio >= 0.001 else ratio

	if is_binary_string(file1_data.decode("latin-1")) and is_binary_string(file2_data.decode("latin-1")):
		start_time = timeit.default_timer()
		ratio = s.quick_ratio()
		elapsed = timeit.default_timer() - start_time
		elapsed_ratio_time[file1] = elapsed
	else:
		try:
			start_time = timeit.default_timer()
			ratio = s.ratio()
			elapsed = timeit.default_timer() - start_time
			elapsed_ratio_time[file1] = elapsed

		except KeyboardInterrupt:
			# if s.ratio() takes too long, press ctrl-c to then use s.real_quick_ratio()
			start_time = timeit.default_timer()
			ratio = s.real_quick_ratio() 
			elapsed = timeit.default_timer() - start_time
			elapsed_ratio_time[file1] = elapsed
	
	return ratio * 100.0
	return ratio * 100.0 if ratio >= 0.001 else ratio

##########################################################################################################

def print_totals(detailed=False, identical=False):
	global count_same_files, count_diff_files, count_unequal_files, count_exclusive_d1, count_exclusive_d2, skipped_files, skipped_directories, elapsed_ratio_time

	dest = sys.stderr
	
	for i in range(0,4): safe_print(outfile=dest)
	safe_print("=" * 135,outfile=dest)
	safe_print("%67s" % ("statistical totals"), outfile=dest)
	safe_print("=" * 135, outfile=dest)
	for i in range(0,2): safe_print(outfile=dest)

	desc = "identical" if identical else "same file metadata"
	safe_print("%40s %s" % ("%s:" % (desc), (count_same_files-count_unequal_files)), outfile=dest)
	safe_print("%40s %s" % ("different files:", count_diff_files), outfile=dest)
	safe_print("%40s %s" % ("same metadata, different data:", count_unequal_files), outfile=dest)
	safe_print("%40s %s" % ("exclusive to directory 1:", count_exclusive_d1), outfile=dest)
	safe_print("%40s %s" % ("exclusive to directory 2:", count_exclusive_d2), outfile=dest)
	safe_print("%40s %s" % ("skipped files (via reg expr):", len(skipped_files)), outfile=dest)
	safe_print("%40s %s" % ("skipped directories (via reg expr):", len(skipped_directories)), outfile=dest)
	for i in range(0,2): safe_print(outfile=dest)

	if not detailed: return

	if len(skipped_files):
		safe_print("skipped files", outfile=dest)
		safe_print("="*13, outfile=dest)
		safe_print(skipped_files, outfile=dest)
		for i in range(0,2): safe_print(outfile=dest)

	if len(skipped_directories):
		safe_print("skipped directories", outfile=dest)
		safe_print("="*19, outfile=dest)
		safe_print(skipped_directories, outfile=dest)
		for i in range(0,2): safe_print(outfile=dest)

	if len(elapsed_ratio_time):
		safe_print("elapsed time for file comparison ratios", outfile=dest)
		safe_print("="*39, outfile=dest)
		sorted_elap = sorted(elapsed_ratio_time.items(), key=operator.itemgetter(1),reverse=True)
		
		for entry in sorted_elap:
			safe_print("[%05.2f] %s" % (entry[1], entry[0]), outfile=dest)
		for i in range(0,2): safe_print(outfile=dest)

##########################################################################################################

def init_tab_file(fname):
	global tab_file, ofmt_delim 
	tab_file = fname

	header = ( "comparison", "dname1", "dname2", "fname", "ratio", "fsize1", "fsize2", "fsize2 - fsize1", "date1", "date2", "date2 - date1 (d:h:m:s)" )
	try:
		with open(tab_file,mode="w",encoding="latin-1") as fp:
			entry = ofmt_delim.join(header)
			fp.write("%s\n" % (entry))
	except OSError as err:
		dest=sys.stderr
		safe_print("",outfile=dest)
		safe_print("Error #5086 - unable to open file for writing: %s" % (fname), outfile=dest)
		safe_print("",outfile=dest)
		safe_print(err,outfile=dest)
		safe_print("",outfile=dest)
		sys.exit(1)


##########################################################################################################

# output file format:
# comparision-type,dname1,dname2,fname,ratio,fsize1,fsize2,fsize_diff,date1,fdate2,date_diff

def save_tab_file(comparison, dname1, dname2, fname, ratio, fsize1, fsize2, date1, date2):
	global tab_file, ofmt_delim, date_time_fmt
	
	if len(dname1):
		d1 = datetime.strptime(date1, date_time_fmt)
	else:
		fsize_diff = ""
		date_diff = ""
		ratio = 0.0

	if len(dname2):
		d2 = datetime.strptime(date2, date_time_fmt)
	else:
		fsize_diff = ""
		date_diff = ""
		ratio = 0.0

	if len(dname1) and len(dname2):
		fsize_diff = fsize2 - fsize1
		op = "" if d2.timestamp() >= d1.timestamp() else "-"
		# http://stackoverflow.com/a/2119509/452281
		tdel = abs( (d2-d1) )
		days, hours, minutes = ( tdel.days, tdel.seconds//3600, (tdel.seconds//60)%60 )
		# http://stackoverflow.com/a/14190143/452281
		seconds = int( tdel.total_seconds() % 60 )

		date_diff = "%s%04d:%02d:%02d:%02d" % (op,days, hours, minutes, seconds)

	with open(tab_file,mode="a",encoding="latin-1") as fp:
		entry = ofmt_delim.join((comparison,dname1,dname2,fname,"%4.2f" % (ratio), "%s" % (fsize1), "%s" % (fsize2), "%s" % (fsize_diff), date1, date2, date_diff))
		fp.write("%s\n" % (entry))

##########################################################################################################

def main():
	global want_verbose_dir_print, shallow_cmp, str_cmp_pgm, only_show_same, html_output_dir, want_ratio_computation

	parser = argparse.ArgumentParser(description="Compare files in two directories", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("dname1", help="first directory to compare")
	parser.add_argument("dname2", help="second directory to compare")
	parser.add_argument("-d", "--diffonly", help="only show files that are different", action="store_true")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-l", "--listdirs", help="recusively list directories to compare", action="store_true")
	group.add_argument("-r", "--recurse", help="recusively view file differences in directories", action="store_true")
	parser.add_argument("-c", "--contents", help="compare contents of the files, not just metadata", action="store_true")
	parser.add_argument("-i", "--identical", help="only show files that have the same metadata",action="store_true")
	parser.add_argument("-p", "--pgm", help="use PGM as your comparision program")
	parser.add_argument("-H", "--hdir", help="output differences to HTML files using HDIR directory")
	parser.add_argument("-n", "--noratio", help="do not compute difference ratio for similar files",action="store_true")
	parser.add_argument("-t", "--tabfile", help="also save tab-delimited results to TABFILE file")
	parser.add_argument("-v", "--verbose", help="print directories being compared to STDERR", action="store_true")
	parser.add_argument("-s", "--stats", help="print statistical totals to STDERR", action="store_true")
	parser.add_argument("-S", "--morestats", help="print even more detailed statistical totals to STDERR", action="store_true")
	
	args = parser.parse_args()

	if args.verbose:
		want_verbose_dir_print = True

	if args.contents:
		shallow_cmp = False

	if args.identical:
		only_show_same = True

	if args.hdir:
		html_output_dir = args.hdir

	if args.noratio:
		want_ratio_computation = False

	if args.pgm:
		str_cmp_pgm = args.pgm
		if -1 == str_cmp_pgm.find('"') and str_cmp_pgm.find(" ") >= 0:
			str_cmp_pgm = '"%s"' % (str_cmp_pgm)
	elif want_cmp_pgm:
		get_default_cmp_pgm()

	if args.listdirs:
		meta = filecmp.dircmp(args.dname1, args.dname2)
		print_listing(meta)
		return 0

	if args.tabfile:
		init_tab_file(args.tabfile)

	if not args.recurse:
		process_directories( args.dname1, args.dname2, diff_only=args.diffonly, recurse=False )
	else:
		process_directories( args.dname1, args.dname2, diff_only=args.diffonly, recurse=True )
		meta =  filecmp.dircmp(args.dname1, args.dname2)
		recurse_directories(meta, args.diffonly)

	if args.stats:
		print_totals(False,args.contents)

	if args.morestats:
		print_totals(True,args.contents)

	return 0

##########################################################################################################

if __name__ == "__main__":
	try:
		rv = main()
	except KeyboardInterrupt:
		rv=130

	sys.exit(rv)

# End of Script
