
# github_create_ini.py
# -John Taylor
# Sept-11-2015

import sys,configparser,os.path,os
from collections import OrderedDict

fname_ini = "gh-__REPO__.ini"
dname_root = ""
numeric_flist = OrderedDict()


##########################################################################

def safe_print(data):
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

##########################################################################

def get_flist(dname="."):

	flist = []
	start = os.path.join(dname_root,dname)
	for root, dirs, files in os.walk(start):
		for fname in files:

			full = os.path.join(root,fname)
			if full.find("%s%s%s" % (os.sep,".git",os.sep)) >= 0: continue
			if fname.lower().find("readme.md") >= 0: continue
			slots = full.split(os.sep)

			# for now, just skip subdirectories
			if len(slots) != 2: continue

			flist.append(fname)
			#print(fname)

	return sorted(flist, key=lambda s:s.lower())

##########################################################################

def make_numeric_list(flist):
	global numeric_flist

	numeric_flist[0] = "-- Quit --"

	n=1
	for fname in flist:
		
		numeric_flist[n] = fname
		n+=1

	for num in numeric_flist:
		safe_print("[%2d] %s" % (num,numeric_flist[num]))

##########################################################################

def main():
	global numeric_flist, fname_ini

	if len(sys.argv) == 1:
		tmp1 = os.path.dirname(os.path.realpath(__file__))
		tmp2 = tmp1.split(os.sep)[-1:][0]
		fname_ini = fname_ini.replace("__REPO__",tmp2)
		
	elif len(sys.argv) == 2:
		fname_ini = fname_ini.replace("__REPO__",sys.argv[1])
	else:
		print(); print("Usage: %s [ repo ]" % (sys.argv[0])); print()
		return 1

	print(); print("ini file: %s" % (fname_ini)); print()


	included_yes = []
	included_no  = []

	repo_files = get_flist()
	
	config = configparser.ConfigParser()
	if os.path.exists(fname_ini):
		config.read(fname_ini)

	for fname in repo_files:
		if fname in config.sections():
			included_yes.append(fname)
		else:
			included_no.append(fname)

	make_numeric_list(included_no)

			
	selection = True
	made_change = False
	while selection:
		print()
		try:
			selection = int(input("Selection: "))
		except:
			selection = False
			break
		if not selection: break
		actual_name = numeric_flist[selection]
		print()

		try:
			with open(actual_name) as fp: lines = fp.read().splitlines()
			max = len(lines) if len(lines) < 9 else 9
			print()
			i = 0
			for line in lines:
				if i >= max: break
				safe_print("\t %s" % (line))
				i+=1
		except:
			pass

		print()

		desc = input("[desc] %s: " % (actual_name))
		if not config.has_section(actual_name):
			config.add_section(actual_name)
		config[actual_name]["desc"] = desc
		if len(desc):
			made_change = True
			included_no.remove(actual_name)
		make_numeric_list(included_no)

	if made_change:
		with open(fname_ini,mode="w",encoding="latin-1") as fp: config.write(fp)

	return 0

##########################################################################

if "__main__" == __name__:
	sys.exit( main() )

