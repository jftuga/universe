#!/usr/bin/env python3

"""
ipinfo.py

Query https://ipinfo.io for IP address info including geographic location when given an IP address, host name or URL
"""

import re
import socket
import sys
import time
import urllib.request

##########################################################################

def resolve(obj):
	n = -1
	try:
		n = socket.gethostbyname_ex(obj)
	except:
		print()
		print("Could not resolve: %s" % (obj))
		print()
		sys.exit(1)

	if type(n) is str:
		return list( [2] )
	else:
		return n[2]

##########################################################################

def get_ip_info(ip:str):
	url = "https://ipinfo.io/%s/json" % (ip)
	text = ""
	try:
		response = urllib.request.urlopen(url)
		data = response.read()
		text = data.decode('utf-8')
	except:
		print()
		print("Could not connect to: %s" % (url))
		print()
		sys.exit(1)
	return text

##########################################################################

def main():
	if len(sys.argv) != 2:
		print("Usage:")
		print("%s: [ IP address | host name | URL ]" % (sys.argv[0]))
		print()
		return

	ip_re = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

	obj = sys.argv[1]

	if obj.find("://") > 1:
		host_name = obj.split("/")[2]
		host_ip_list = resolve( host_name )
	else:
		match = ip_re.findall(obj)

		if len(match):
			host_ip_list = match
		else:
			host_ip_list = resolve( obj )

	for ip in host_ip_list:
		print( get_ip_info(ip))
		if(len(host_ip_list) > 1):
			time.sleep(0.25)

##########################################################################

if __name__ == '__main__':
	main()

