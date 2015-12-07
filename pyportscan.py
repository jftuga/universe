#!/usr/bin/env python3

# A simple port scanner

import socket
import sys
from datetime import datetime


# Check what time the scan started
t1 = datetime.now()

# Using the range function to specify ports (here it will scans all ports between 1 and 1024)

# We also put in some error handling for catching errors

for octet in range(1,254):
	remoteServerIP = "192.168.1.%s" % (octet)
	#print(remoteServerIP)
	for port in (22,80,443):
		try: 
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(0.2)
			result = sock.connect_ex((remoteServerIP, port))
			if result == 0:
				print("{} Port {}: \t Open".format(remoteServerIP, port))
			sock.close()

		except KeyboardInterrupt:
			print("You pressed Ctrl+C")
			sys.exit()

		except socket.gaierror:
			print('Hostname could not be resolved. Exiting')
			sys.exit()

		except socket.error:
			print("Couldn't connect to server")
			sys.exit()

# Checking the time again
t2 = datetime.now()

# Calculates the difference of time, to see how long it took to run the script
total =	t2 - t1

# Printing the information to screen
print('Scanning Completed in: ', total)

