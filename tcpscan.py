#!/usr/bin/env python3

"""
tcpscan.py 
-John Taylor

A simple, multi-threaded TCP port scanner
"""

import sys
import socket
import argparse
import concurrent.futures
from collections import defaultdict
from datetime import datetime
from ipaddress import ip_network
from random import shuffle

pgm_version = "1.08"
pgm_date = "Jan-15-2016 06:09"

# default maximum number of concurrent threads, changed with -T
max_workers = 50

# default connect timeout when checking a port, changed with -t
connect_timeout = 0.07

# list of ports to scan if -p is not given on the command line
default_port_list = "20,21,22,23,25,47,53,69,80,110,113,123,135,137,138,139,143,161,179,194,201,311,389,427,443,445,465,500,513,514,515,530,548,554,563,587,593,601,631,636,660,674,691,694,749,751,843,873,901,902,903,987,990,992,993,994,995,1000,1167,1234,1433,1434,1521,1528,1723,1812,1813,2000,2049,2375,2376,2077,2078,2082,2083,2086,2087,2095,2096,2222,2433,2483,2484,2638,3000,3260,3283,3306,3389,3478,3690,4000,5000,5432,5433,6000,6667,7000,8000,8080,8443,8880,8888,9000,9001,9418,9998,27017,27018,27019,28017,32400"

# initialize other globals...
active_hosts = defaultdict(list)
hosts_scanned = 0
skipped_hosts = 0
skipped_ports = 0
opened_ports = 0
ports_scanned = 0
skipped_port_list = []

#############################################################################################

def scan_one_host(ip,ports):
	global args, max_workers, connect_timeout, hosts_scanned

	hosts_scanned += 1
	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		if end < start:
			print("\nError: For -p option, ending port is less that starting port\n")
			sys.exit(1)		
		port_list = list(range(start,end+1))
	else:
		# comma separated list of ports, can also include a single port
		port_list = ports.split(",")
		
	if args.shuffleports: shuffle(port_list)
	with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
		alpha = {executor.submit(scan_one_port, ip, current_port): current_port for current_port in port_list}
		for future in concurrent.futures.as_completed(alpha):
			pass

#############################################################################################

def scan_one_port(ip,port):
	global args, fp_output, active_hosts, opened_ports, ports_scanned
	global max_workers, connect_timeout, skipped_port_list, skipped_ports
	port = int(port)

	if port in skipped_port_list:
		if args.verbose:
			line = "{}\t{}\tport-excluded".format(ip,port)
			print(line)
			if args.output: fp_output.write("%s\n" % (line.replace("\t",",")))
		skipped_ports += 1
		return False

	try: 
		ports_scanned += 1
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

	except socket.error:
		print("Couldn't connect to server %s on port %s" % (ip,port))
		return False

#############################################################################################

def create_skipped_port_list(ports):
	global skipped_port_list 

	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		if end < start:
			print("\nError: For -X option, ending port is less that starting port\n")
			sys.exit(1)
		skipped_port_list = list(range(start,end+1))
	else:
		# comma separated list of ports, can also include a single port
		skipped_port_list = [int(n) for n in ports.split(",")]

#############################################################################################

def main():
	global args, fp_output, default_port_list
	global max_workers, connect_timeout
	global skipped_hosts, skipped_ports, hosts_scanned

	parser = argparse.ArgumentParser(description="tcpscan.py: a simple, multi-threaded TCP port scanner", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("target", help="e.g. 192.168.1.0/24 192.168.1.100 www.example.com")
	parser.add_argument("-x", "--skipnetblock", help="skip a sub-netblock, e.g. 192.168.1.96/28")
	parser.add_argument("-X", "--skipports", help="exclude a subset of ports, e.g. 135-139")
	parser.add_argument("-p", "--ports", help="comma separated list or hyphenated range, e.g. 22,80,443,445,515  e.g. 80-515")
	parser.add_argument("-T", "--threads", help="number of concurrent threads, default: %s" % (max_workers))
	parser.add_argument("-t", "--timeout", help="number of seconds to wait for a connect, default: %s" % (connect_timeout))
	parser.add_argument("-s", "--shufflehosts", help="randomize the order IPs are scanned", action="store_true")
	parser.add_argument("-S", "--shuffleports", help="randomize the order ports are scanned", action="store_true")
	parser.add_argument("-c", "--closed", help="output ports that are closed", action="store_true")
	parser.add_argument("-o", "--output", help="output to CSV file")
	parser.add_argument("-v", "--verbose", help="output statistics", action="store_true")

	args = parser.parse_args()

	if args.threads:
		max_workers = int(args.threads)
	if args.timeout:
		connect_timeout = float(args.timeout)
	if args.output:
		fp_output = open(args.output,mode="w",encoding="latin-1")
	if args.skipports:
		create_skipped_port_list(args.skipports)
	
	port_list = args.ports if args.ports else default_port_list
	ip_skiplist = ip_network(args.skipnetblock) if args.skipnetblock else []

	if any(c.isalpha() for c in args.target):
		try:
			ip = socket.gethostbyname(args.target)
			hosts = (ip,)
		except:
			print("Unable to resolve hostname:", args.target)
			sys.exit(1)
	else:
		try:
			tmp = ip_network(args.target)
		except ValueError as err:
			print("Error:", err)
			sys.exit(1)

		hosts = list(tmp.hosts())
		if args.shufflehosts:
			shuffle(hosts)
		
		if not len(hosts): # a single ip-address was given on cmd-line
			tmp = args.target.replace("/32","")
			hosts = (tmp,)
	
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
		try:
			scan_one_host( "%s" % (my_ip), port_list )
		except KeyboardInterrupt:
			print("\nYou pressed Ctrl+C")
			sys.exit(1)

	t2 = datetime.now()
	total =	t2 - t1

	if args.verbose:
		print()
		print("Scan Time    : ", total)
		print("Active Hosts : ", len(active_hosts))
		print("Hosts Scanned: ", hosts_scanned)
		print("Skipped Hosts: ", skipped_hosts)
		print("Opened Ports : ", opened_ports)
		print("Skipped Ports: ", skipped_ports)
		print("Ports Scanned: ", ports_scanned)
		print()
	else:
		if not opened_ports:
			print()
			print("Opened Ports : ", opened_ports)
			print("Hosts Scanned: ", hosts_scanned)
			print("Ports Scanned: ", ports_scanned)
			print()

	if args.output:
		fp_output.close()

#############################################################################################

if "__main__" == __name__:
	main()

