#TEXTCHARS = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))

import sys

def safe_print(data):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )


TEXTCHARS = ''.join(map(chr, [7,8,9,10,12,13,27]))
for i in range(0x20, 0x100):
	TEXTCHARS += chr(i)

ALLBYTES = ''.join(map(chr, range(256)))

safe_print( len( TEXTCHARS))
print( len( ALLBYTES))