
# copy_atime_mtime.py
# -John Taylor
# Aug-13-2015

import os,sys

# copies the src atime/mtime (access/modifiy) attribs to dst
# ctime can not be changed

src = sys.argv[1]
dst = sys.argv[2]

meta = os.stat(src)
os.utime(dst, (meta.st_atime,meta.st_mtime))

print( os.stat(src) )
print( os.stat(dst) )
