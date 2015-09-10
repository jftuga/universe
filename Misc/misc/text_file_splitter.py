#!/usr/local/bin/python3
"""
text_file_splitter.py
Jun-19-2012
-John Taylor

Python 3.2
"""

import sys,math

if len(sys.argv) != 4 and len(sys.argv) !=5:
	print()
	print("Splits a text file in to multiple files.")
	print()
	print("Usage:")
	print("%s  [# of lines per file]  [input file]  [output file]  [output file ext]" % (sys.argv[0]))
	print("\t the last argument is optional; it should begin with a dot")
	print()
	sys.exit()

size = int(sys.argv[1])
finput = sys.argv[2]
foutput = sys.argv[3]
if len(sys.argv) == 5:
	exten = sys.argv[4]
else:
	exten = ""

infp = open(finput,encoding="latin-1")

end = size
curr = 1

fname="%s-%05d%s" % (foutput,curr,exten)
print("Writing lines: [% 5d ... % 5d] to file: %s" % (1,size,fname))
outfp=open(fname,mode="w",encoding="latin-1")

for n, line in enumerate(infp):
	if n >= end:
		outfp.close()
		curr = curr + 1
		end = curr * size
		fname="%s-%05d%s" % (foutput,curr,exten)
		print("Writing lines: [% 5d ... % 5d] to file: %s" % (n,end,fname))
		outfp=open(fname,mode="w",encoding="latin-1")

	print(line, end="",file=outfp)

if not outfp.closed:
	outfp.close()
