#!/usr/bin/env python3

"""
tc_try.py
Jan-21-2016

This program tries to guess your truecrypt password if you don't
remember all of your password but do remember most or at least
some of it.

Here is the scenario in which this worked for me.  TC prefers a 20
character or longer password.  I usually have a handful of passwords
that I use. So for my TC password, I strung 3 or 4 of these together.
The problem was that I could not remember which passwords I used, or
which order.  Hence, the birth of this script. :-)

For example, lets say you made your password from 4 words in the NATO
alphabet: https://en.wikipedia.org/wiki/NATO_phonetic_alphabet

Your forgotten TC container password is: kiloechosierrabravo
                                         (kilo echo sierra bravo)

Since you don't remember your password, you can create a pwlist file
containing all 26 NATO words.  This program will iterate through all
possible permutations of 4 words in the pwlist and then 3 words in the
list and then 2 and then 1.  The maximum length of words to combine is
set with the 'pwlen' variable.  The shorter your pwlist is, the quicker
this script will run.  So if you are confident that a word is not used
within your full password, then you should not include it in your
pwlist file.

If you want to try BRAVO, Bravo and bravo then you will need to have all
3 of these words listed in your pwlist file.  In the run_pgm() function,
you can further narrow down your search list by checking for first
character of password, length of password, etc.  See the run_pgm() 
function code for more details.

See this web page to see how the password lists are generated:
https://docs.python.org/3.5/library/itertools.html#itertools.permutations
It is quicker to put the more probable password entries towards the
top of the pwlist file.

This program depends on Python 3.5 and the NumPy extension. I installed
NumPy on Windows 7 from:
http://www.lfd.uci.edu/~gohlke/pythonlibs/

Variables that you will need to configure:
pgm, max_workers, fname_pwlist, pwlen, tcfile, and drive_mount_letter
optional: keyfile

Good Luck!

"""

import itertools, os, os.path, sys, time
import concurrent.futures, random, numpy
import subprocess, shlex

pgm_version = "2.01"
pgm_date = "Jan-22-2016 09:32"

#############################################################################

# location of the TC executable
pgm = 'C:\\Program Files\\TrueCrypt\\TrueCrypt.exe'

# for veracrypt:
# but not recommended as multithreading does not really work well
#hash_type = "whirlpool"
#cmd = '"%s" /m ro /q /s /k %s /l %s /v %s /hash %s /p ' % (pgm, keyfile, drive_mount_letter, tcfile, hash_type)

# number of concurrent passwords to try
# start off with either 2x or 4x the number of CPU cores
max_workers=8

# a list of passwords, one per line
# these will be concatenated togther up to 'pwlen' words
fname_pwlist = 'c:\\tc\\pwlist.txt'

# will take all sets of this number of entries from pwlist and try them in every possible combination
pwlen = 4

# the actual truecrype file you are trying to mount
# note the number of backslashes needs to be doubled since this runs in a subprocess()
tcfile = 'C:\\\\tc\\\\test_container.tc'

# when trying password, what drive letter to mount the TC volume to
drive_mount_letter = 'q'
drive_mount_point = '%s:\\nul' % (drive_mount_letter)

# truecrypt command line args
# if you use a keyfile add /k %s before the /p
#keyfile = 'c:\\\\tc\\\\secure.key'
cmd = '"%s" /m ro /q /s /l%s /v %s /p ' % (pgm, drive_mount_letter, tcfile)
dismount_cmd = '"%s" /d /l%s /s /q' % (pgm, drive_mount_letter)

# a checkpoint file will periodically save where you are at within the pwlist
# if a checkpoint file exists when restarting, the password attempts will
# resume from the last checkpoint
checkpoint_groups = 10
checkpoint_fname = "%s.chkpt" % (tcfile)

# other globals

# since the script tries passwords in parallel, it it hard to tell which one
# of the possible set of 'max_workers' subprocesses actually succeeded in mounting
# the container 

# when a possible password is found from one of the subprocesses, set this to true
eureka = False

# a list of all possible passwords that could be the correct password
# this length is no longer than 'max_workers'
candidates = {}

# the number of passwords that have been attempted
attempts = 0

#############################################################################

def is_mounted():
	try:
		#print("is_mounted(): %s" % (drive_mount_point))
		#print("checking for:", drive_mount_point)
		open( drive_mount_point, "r")
	except IOError:
		return False
	else:
		return True

#############################################################################

# at this point, the container is successfully mounted, but the script
# is not sure which one of the 'max_worker' subprocesses was successful
# step through each candidate (not in parallel) until the correct candidate
# is discovered
def get_pw_from_candidates():
	global eureka, attempts

	eureka = False

	# unmount the containter
	args = shlex.split(dismount_cmd)
	proc=subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)

	# single-threaded check
	for pw in candidates:
		attempts += 1
		rv = run_pgm(pw,True)
		if 2 == rv:
			break

#############################################################################

# this is running in it's own thread
# it is the function that actually executes the TC command will all of 
# the necessary command line options and password to try
def run_pgm(curr_pass,final_pass=False):
	global eureka, candidates, attempts
	
	if eureka:
		return

	"""
	this is a good place to add code that will
	skip passwords that you know are not correct

	#if you know the password begins with a 'g'...
	if curr_pass[0] != 'g':
		return

	#if you know the password ends in a '0'...
	if curr_pass[-1] != '0':
		return

	#if you know the password length is at least 14 characters long...
	if len(curr_pass) < 14:
		return
	"""
	
	cmd_final = '%s %s' % (cmd, curr_pass)
	args = shlex.split(cmd_final)
	print(args)
	
	proc=subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
	attempts += 1
	
	if 0 == proc.returncode:
		eureka = True
		if not final_pass:
			print("possible solution: ", curr_pass)
			candidates[curr_pass] = 1
		else:
			print()
			print("="*77)
			print("\nEureka!\n")
			print("Truecrypt password is: %s\n" % (curr_pass))
			print("%d password attempts were made." % (attempts))
			return 2
		return 0

#############################################################################

# all possible passwords are broken up into chunks of max_worker length
def guess_one_group(passwd_grp):
	with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
		alpha = { executor.submit(run_pgm, "".join(curr_pass)): curr_pass for curr_pass in passwd_grp }
		for future in concurrent.futures.as_completed(alpha):
			pass

#############################################################################

# script exection starts here
def main():
	global eureka, attempts, pwlen

	if is_mounted():
		print( "%s is already mounted, program aborted." % (drive_mount_letter))
		return 2

	if not os.path.isfile( tcfile ):
		print()
		print( "Cannot open file: %s" % (tcfile))
		print( "program aborted.")
		return 2

	if not os.path.isfile( pgm ):
		print
		print( "Cannot open file: %s" % (pgm))
		print( "program aborted.")
		return 2	

	print()
	print("tc_try.py")
	print("-" * 9)
	print("pgm_version : %s" % (pgm_version))
	print("pgm_date    : %s" % (pgm_date))
	print()

	start_time = time.localtime()
	end_time = False
	with open(fname_pwlist) as fp: pw_fragment_list = fp.read().splitlines()
	print("password fragments loaded from %s: %d" % (fname_pwlist, len(pw_fragment_list)) )
	if os.path.exists( checkpoint_fname ):
		with open(checkpoint_fname) as fp: checkpoint_list = fp.read().splitlines()
		last = checkpoint_list[-1]
		old_timestamp,old_pwlen,move_to_chk_num,old_attempts = last.split("\t")
		pwlen = int(old_pwlen)
		print("checkpoint file found, continuing from last checkpoint location of %s:%s\n" % (pwlen,move_to_chk_num))
		move_to_chk_num = int(move_to_chk_num) - 1
	else:
		move_to_chk_num = 0
		print()

	# main processing loop
	for curr_pwlen in range(pwlen,0,-1):
		print("="*20, "trying password of group length: %d" % (curr_pwlen))

		items = itertools.permutations(pw_fragment_list, curr_pwlen)
		passwd_list = numpy.array_split( list(items), checkpoint_groups)

		chk = 0
		for grp in passwd_list:
			if eureka: break
			if move_to_chk_num:
				chk += 1
				move_to_chk_num -= 1
				continue
			chk +=1

			now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			print("[%s] group length: %s checkpoint: %s" % (now,curr_pwlen,chk))
			guess_one_group(grp)
			now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			with open(checkpoint_fname,mode="a") as fp: fp.write("%s\t%s\t%s\t%s\n" % (now,curr_pwlen,chk,attempts))

		if eureka:
			get_pw_from_candidates()
			end_time = time.localtime()
			break
	
	if not end_time:
		end_time = time.localtime()
		
	print()
	print("="*77)
	print()
	print( "start time: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", start_time)))
	print( "end time  : %s" % (time.strftime("%Y-%m-%d %H:%M:%S", end_time)))
	print()
	if not eureka:
		print("Unable to guess the password for: %s" % (tcfile))
		print("%s passwords were attempted.\n" % (attempts))
		return 1

	return 0

#############################################################################

if "__main__" == __name__:
	sys.exit(main())

# end of script
