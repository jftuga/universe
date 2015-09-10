
# get_device_type.py
# -John Taylor
# Jun-26-2015

# simplistic method of determining a device type given it's IP address
# it checks for open ports listed in "device"

import sys, socket
from collections import OrderedDict

def get_device_type(ip):
	device = OrderedDict()

	device["windows"] = (139,445)
	device["pcoip"] = (427,443)
	device["printer"] = (515,9100)

	success = False
	for dtype in device.keys():
		if success:
			break
		success_count = 0
		success_len = len(device[dtype])
		for port in device[dtype]:
			print("Scanning ip: %s port: %s" % (ip,port))
			sock = socket.socket()
			sock.settimeout(1.5)
			try:
				sock.connect( (ip,port) )
			except (socket.timeout,ConnectionRefusedError) as err:
				print("conn status:", err)
			else:
				success_count += 1
				print("conn status: OK")

				if success_len == success_count:
					success = True
					detected = dtype


	if success:
		print("[%s] detected device type: %s" % (ip,detected))
		return detected
	else:
		print("[%s] could not determine device type." % (ip))
		return False


if __name__ == "__main__":
	if 2 != len(sys.argv):
		print()
		print("Usage:")
		print("%s [ ip address ]" % (sys.argv[0]))
		print()
		sys.exit()

	get_device_type( sys.argv[1])
