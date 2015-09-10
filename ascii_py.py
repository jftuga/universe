import sys

def safe_print(data):
     print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

print()
print( "dec \t chr \t hex \t oct")
print( "=== \t === \t === \t ===")
for i in range(0,255+1):
	ch = chr(i)
	if 7==i or 9==i or  10==i or 13==i:
		ch = "n/a"
	safe_print( "%d \t %s \t %s \t %s" % (i, ch, hex(i), oct(i)))
print()
