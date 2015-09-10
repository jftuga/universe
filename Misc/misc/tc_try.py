
"""
tc_try.py
Jun-27-2010

This program tries to guess your truecrypt password if you forget it.
Here is the scenario in which this worked for me.  TC prefers a 20
character or longer password.  I usually have a handful of passwords
that I use. So for my TC password, I strung 3 or 4 of these together.
The problem was that I could not remember which passwords I used, or
which order.  Hence, the birth of this script. :-)

See this web page to see how the password lists are generated:
http://docs.python.org/library/itertools.html#itertools.permutations
It is quicker to put the more probable password entries towards the
top of the pwlist file.

This script is very slow... good luck!

variables:
pwlist - enter all of your passwords in this file, one per line
pwlen  - how many entries in pwlist to concatenate together
tcfile - the truecrypt file you want to mount
drvltr - which drive letter to mount
"""

#############################################################################

pwlist = r'c:\pwlist.txt'
pwlen = 3    # will take all sets of 3 entries (and less) from pwlist
             # and try them in every possible combination
tcfile = r'c:\data.tc'
drvltr = 'j'


status = "%s.status" % (tcfile)
pgm = r'C:\Program Files\TrueCrypt\truecrypt.exe'
cmd = '"%s" /m ro /q /s /l%s /v %s /p ' % (pgm, drvltr, tcfile)
test = r'%s:\nul' % (drvltr)

#############################################################################

import itertools, os, os.path, sys, time

plist = file( pwlist ).readlines()
items = itertools.permutations(plist, pwlen)

try:
	open( test, "r")
except IOError:
	pass
else:
	print
	print "%s is already mounted, program aborted." % (drvltr)
	sys.exit()

if not os.path.isfile( tcfile ):
	print
	print "Cannot open file: %s" % (tcfile)
	print "program aborted."
	sys.exit()

if not os.path.isfile( pgm ):
	print
	print "Cannot open file: %s" % (pgm)
	print "program aborted."
	sys.exit()

print
print "tc_try.py"
print "---------"
print "calculating total number of guesses to be made (may take awhile to compute)"
print
max=0
for i in items:
	max += pwlen
items = itertools.permutations(plist, pwlen)

update = float(max) * 0.05
update = int(update)
if update < 5:
	update = 5
if update > 100:
	update = 100

print "%d passwords in file: %s" % (len(plist), pwlist)
print "%d password guesses will be made" % (max)
print "status updates every %d guesses" % (update)
print

#############################################################################

print
print "start time: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print

n = 0
start = time.time()
for i in items:
	pw = ""
	for j in i:
		pw = "%s%s" % (pw, j[:-1])
		n += 1
		os.system( cmd + pw )
		try:
			open( test, "r")
		except IOError:
			if 0 == ( n % update ):
				elapsed = time.time() - start
				estimated_remaining = elapsed * (max * 1.0) / n
				estimated_end_time = time.time() + estimated_remaining
				print "%d guesses made so far : ( %s )" % (n,pw)
				print "elapsed time (in mins)    : ( %.2f )" % (elapsed / 60.0)
				print "estimated end time        : ( %s )" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(estimated_end_time)))
				print
				#possible future enhancement: allow the script to restart where it left off
				#file(status,"w").write("%s\n" % n)
		else:
			elapsed = time.time() - start
			print
			print
			print "Eureka! :-)"
			print "%s is mounted on %s: with password: %s" % ( tcfile, drvltr, pw)
			print "%d guesses were made." % (n)
			print "%.2f minutes elapsed." % ( elapsed / 60.0)
			print "end time: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
			sys.exit()

#
# end of loop
#
elapsed = time.time() - start
print
print
print "Bummer."
print "Did not find the truecrypt password :-("
print "The last guess was: %s" % (pw)
print "%d guesses were made." % (n)
print "%.2f minutes elapsed." % ( elapsed / 60.0)
print "end time: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(estimated_end_time)))
sys.exit()

