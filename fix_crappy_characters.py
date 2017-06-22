
"""
fix_crappy_characters.py
-John Taylor
May-6-2011
Jun-22-2017: Updated for Python 3

Sometimes copying & pasting from a web page can screw up punctuation characters.  
This script fixes that!  You may need to add more values to the 'fix' table.
The key in the 'fix' dictionary is the ascii decimal value of the bad character.
"""

import sys

fix = { 133: ".", 145: "'", 146: "'", 147: '"', 148: '"', 150: "-", 151: "-" }

express = "line"
for subst in fix:
	if fix[subst] != "'":
		express += ".replace('%c','%c')" % (chr(subst),ord(fix[subst]))
	else:
		express += '.replace("%c","%c")' % (chr(subst),ord(fix[subst]))
#print "\n%s\n" % (express)
#sys.exit()

if len(sys.argv) == 3 and sys.argv[1] == "-s":
	summary = 1
	fname = sys.argv[2]
elif len(sys.argv) == 2:
	summary = 0
	fname = sys.argv[1]
else:
	print()
	print("Usage: %s [-s] [ filename ]" % sys.argv[0])
	print("Optional -s : prints a summary of the bad characters, with line numbers")
	print()
	print("Use -s first, and then rinse & repeat. :-)")
	print()
	sys.exit()

data = open(fname,"r",encoding="utf-8").readlines()

if 1 == summary:
	count = 0
	linenum = 1
	for line in data:
		line = line[:-1]
		for ch in line:
			if ord(ch) >= 127:
				print("[%d] (%d)%c : %s" % (linenum, ord(ch), ch, line))
				count += 1
		linenum +=1

	if 0 == count:
		print()
		print("File is clean - no crappy characters found!")
		print()
	else:
		print()
		print("%d crappy characters found :-(" % (count))
		print()

	sys.exit()

if 0 == summary:
	for line in data:
		line = line[:-1]
		result = eval(express)
		print(result)


