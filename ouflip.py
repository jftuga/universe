
"""

ouflip.py
-John Taylor
May-19-2011
Feb-2-2012 (Python 3)


input
dev.example.com/Departments/Supp Services/Marketing

output
"OU=Marketing,OU=Supp Services,OU=Departments,DC=dev,DC=example,DC=com"
"""

import sys

arg  = " ".join(sys.argv[1:])
slots = ("DC=" + arg.replace(".","/DC=")).split("/")
domain = slots[0:3]
path   = slots[3:]

slots = []
for i in range(len(path),0,-1):
	tmp = "OU=" + path[i-1]
	slots.append(tmp)

flipped = ",".join((slots + domain))

print()
print( '"%s"' % (flipped) )
print()
print( 'adfind -b "%s" -f "objectcategory=computer" 2>nul | mawk -F"=|," "$0 ~ /dn:/ {print $2}" | gsort -n' % (flipped))
print()

