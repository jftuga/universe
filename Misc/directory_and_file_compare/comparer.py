
import cPickle,sys
from collections import defaultdict,OrderedDict,namedtuple

fname_mst = r'2tb\2tb.pkl'
fname_slv = r'slave\slave.pkl'

dentry = namedtuple("dentry","ditems dsize")

fp1 = open(fname_mst,"rb")
mst = cPickle.load(fp1)
fp1.close()


fp2 = open(fname_slv,"rb")
slv = cPickle.load(fp2)
fp2.close()

print "-" * 99

count = 0
i = 0
f = 0

for entry in slv:
	count += 1
	slots=entry.split("+++")
	genre = slots[0]
	artist = slots[1]
	album = slots[2]

	ga = "%s+%s" % (genre,album)

	if genre not in mst:
		print genre

sys.exit(0)

for entry in slv:
	count += 1
	slots=entry.split("+++")
	genre = slots[0]
	artist = slots[1]
	album = slots[2]

	if mst[entry].ditems <> slv[entry].ditems:
		print "item count mismatch:", entry
	elif mst[entry].dsize <> slv[entry].dsize:
		print "file size mismatch :", entry

	i += mst[entry].ditems
	f += mst[entry].dsize

print
print count, "items checked."
print i, " ditems"
print f, " dsize"
