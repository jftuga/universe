#!/usr/bin/env python3

"""
tcpscan.py 
-John Taylor

A simple, multi-threaded TCP port scanner
"""

import socket
import argparse
import concurrent.futures
from collections import defaultdict
from datetime import datetime
from ipaddress import IPv4Address,ip_network
from random import shuffle

pgm_version = "1.00"
pgm_date = "Dec-8-2015 16:36"

# default maximum number of concurrent threads, changed with -T
max_workers = 50

# default connect timeout when checking a port, changed with -t
connect_timeout = 0.07

# initialize other globals...
active_hosts = defaultdict(list)
skipped_hosts = 0
skipped_ports = 0
opened_ports = 0
skipped_port_list = []

#############################################################################################

def scan_one_host(ip,ports):
	global max_workers, connect_timeout
	
	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
			alpha = {executor.submit(scan_one_port, ip, current_port): current_port for current_port in range(start,end+1)}
			for future in concurrent.futures.as_completed(alpha):
				pass
	else:
		# comma separated list of ports, includes just one port
		port_list = ports.split(",")
		with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
			beta = {executor.submit(scan_one_port, ip, current_port): current_port for current_port in port_list}
			for future in concurrent.futures.as_completed(beta):
				pass

#############################################################################################

def scan_one_port(ip,port):
	global args, fp_output, active_hosts, opened_ports
	global max_workers, connect_timeout, skipped_port_list, skipped_ports
	port = int(port)

	if port in skipped_port_list:
		if args.verbose:
			line = "{}\t{}\tport-excluded".format(ip,port)
			print(line)
			if args.output: fp_output.write("%s\n" % (line.replace("\t",",")))
		skipped_ports += 1
		return

	try: 
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(connect_timeout)
		result = sock.connect_ex((ip, port))
		
		if result == 0:
			valid = True
			opened_ports += 1
			active_hosts[ip].append(port)
			line = "{}\t{}\topen".format(ip, port)
			print(line)
			if args.output: fp_output.write("%s\n" % (line.replace("\t",",")))
		else:
			valid = False
			if args.closed: 
				line = "{}\t{}\tclosed".format(ip, port)
				print(line)
				if args.output: fp_output.write("%s\n" % (line.replace("\t",",")))
			
		sock.close()
		return valid

	except KeyboardInterrupt:
		print("You pressed Ctrl+C")
		return False

	except socket.gaierror:
		print('Hostname could not be resolved')
		return False

	except socket.error:
		print("Couldn't connect to server")
		return False

#############################################################################################

def create_skipped_port_list(ports):
	global skipped_port_list 

	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		skipped_port_list = list(range(start,end+1))
	else:
		# comma separated list of ports, includes just one port
		skipped_port_list = ports.split(",")


#############################################################################################

def main():
	global args, fp_output
	global max_workers, connect_timeout
	global skipped_hosts, skipped_ports

	parser = argparse.ArgumentParser(description="Network port scanner", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("netblock", help="example: 192.168.1.0/24")
	parser.add_argument("-x", "--skipnetblock", help="skip a sub-netblock, example: 192.168.1.96/28")
	parser.add_argument("-X", "--skipports", help="exclude a subset of ports, example: example: 135-139")
	parser.add_argument("-p", "--ports", help="comma separated list or hyphenated range, example: 22,80,443,445,515  example: 80-515")
	parser.add_argument("-T", "--threads", help="number of concurrent threads, example: 25")
	parser.add_argument("-t", "--timeout", help="number of seconds to wait for a connect, example: 0.2")
	parser.add_argument("-s", "--shuffle", help="randomize the order IPs are scanned", action="store_true")
	parser.add_argument("-c", "--closed", help="output ports that are closed", action="store_true")
	parser.add_argument("-o", "--output", help="output to CSV file")
	parser.add_argument("-v", "--verbose", help="output more statistics", action="store_true")

	args = parser.parse_args()

	if args.threads:
		max_workers = int(args.threads)
	if args.timeout:
		connect_timeout = float(args.timeout)
	if args.output:
		fp_output = open(args.output,mode="w",encoding="latin-1")
	if args.skipports:
		create_skipped_port_list(args.skipports)

	ip_skiplist = ip_network(args.skipnetblock) if args.skipnetblock else []

	tmp = ip_network(args.netblock)
	hosts = list(tmp.hosts())
	if args.shuffle:
		shuffle(hosts)

	t1 = datetime.now()
	for tmp in hosts:
		my_ip = "%s" % (tmp)
		if tmp in ip_skiplist:
			if args.verbose:
				line = "{}\tn/a\thost-excluded".format(my_ip)
				print(line)
				if args.output: fp_output.write("%s\n" % (line.replace("\t",",")))
			skipped_hosts += 1
			continue
		scan_one_host( "%s" % (my_ip), args.ports )

	t2 = datetime.now()
	total =	t2 - t1

	if args.verbose:
		print()
		print("Scan Time    : ", total)
		print("Active Hosts : ", len(active_hosts))
		print("Skipped Hosts: ", skipped_hosts)
		print("Opened Ports : ", opened_ports)
		print("Skipped Ports: ", skipped_ports)
		print()

	if args.output:
		fp_output.close()

#############################################################################################

if "__main__" == __name__:
	main()
