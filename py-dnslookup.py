#!/usr/bin/env python3
import sys, socket, re

def resolve(ip):
	n = -1
	try:
		n = socket.gethostbyname(ip)
	except:
		return -1

	return n


ip_re = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")


obj = sys.argv[1]

if obj.find("://") > 1:
	host_name = obj.split("/")[2]
	host_ip = resolve( host_name )
else:
	match = ip_re.findall(obj)
	if len(match):
		host_ip = match[0]
	else:
		host_ip = resolve( obj )

print(host_ip)
