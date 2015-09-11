#!/usr/bin/env python3

import math

def main():
	max=120000000
	
	total = 0
	for i in range(1,max+1):
		total += 1 / (i*i)

	print()
	print(total)
	print("1.64493406684822643647241516664602518921")
	print()
	print( (math.pi**2) / 6)


main()
