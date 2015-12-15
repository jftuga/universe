#!/usr/bin/env python3

# randomly_select_lines.py
# -John Taylor
# Dec-15-2015

# randomly select lines from an input file matching your criteria
# see the is_valid() function

import sys, random, argparse

pgm_version = "1.00"
pgm_date = "Dec-15-2015 16:05"
used = {}
tries = 0

#############################################################################

# convert any unicode characters to something that can be displayed in the console window
def safe_print(data):
	print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

#############################################################################

# define your own validation here
# isalpha() returns true only if each character is a string
def is_valid(line):
	return line.isalpha() and len(line) >= 5 and len(line) <= 11

#############################################################################

# do not return a duplicate line
def get_unused(max_index):
	global used, tries

	if tries > (max_index*20): # increase this constant to search for a longer time period
		print();print("Error: Search exhasted, avoiding infinite loop or a very long run-time."); print()
		sys.exit(1)

	while True:
		n = random.randint(0,max_index)
		tries+=1
		if n in used: continue
		break
	used[n]= 1

	return n

#############################################################################

def get_lines(fname, count):
	with open(fname) as fp: lines = fp.read().splitlines()
	max_index = len(lines) - 1
	random.seed()

	used = {}
	for i in range(0,count):
		while True:
			n = get_unused(max_index)
			if is_valid(lines[n]):
				safe_print(lines[n])
				break

#############################################################################

def main():
	
	parser = argparse.ArgumentParser(description="randomly select lines from an input file", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("fname", help="input filename")
	parser.add_argument("num", help="number of lines to select")
	args = parser.parse_args()

	get_lines(args.fname, int(args.num))
	
	#uncomment if you want to see the number of iterations needed to complete the list
	#print(); print(tries)
	return 0

#############################################################################

if "__main__" == __name__:
	sys.exit( main() )
