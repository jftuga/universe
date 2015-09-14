
import random, sys, array

max_mem = 256 * (1024 ** 2)
size = 5 * (1024 ** 3)


def create_data(size):
	data_array = array.array("c")
	for i in range(0,size):
		data_array.append( "%c" % random.randint(0,255) )
	return data_array

def main():
	random.seed()
	fp=file("blob.dat","a")
	slots = size / max_mem
	print "slots:", slots
	for i in range(0,slots):
		create_data(max_mem).tofile(fp)
		print "%4.2f complete" % (100* ((i+1) / (1.0*slots)))
	fp.close()

main()


