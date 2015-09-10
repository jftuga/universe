# read a file into a line-by-line array, stripping new line chars
with open(fname) as fp: lines = fp.read().splitlines()
