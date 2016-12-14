#!/usr/bin/env python3

"""
tcpscan.py 
-John Taylor

A simple, multi-threaded IPv4 TCP port scanner for Python 3.5

For help, run: tcpscan.py -h

"""

import sys
import socket
import socketserver
import argparse
import time
import ipaddress
import concurrent.futures
from collections import defaultdict
from datetime import datetime
from random import shuffle

pgm_version = "1.19"
pgm_date = "Dec-14-2016 12:41"

# default maximum number of concurrent threads, changed with -T
max_workers = 50

# default connect timeout when checking a port, changed with -t
connect_timeout_lan = 0.07
connect_timeout_wan = 0.18
connect_timeout = 0

# list of ports to scan if -p is not given on the command line
default_port_list = "20,21,22,23,25,47,53,69,80,110,113,123,135,137,138,139,143,161,179,194,201,311,389,427,443,445,465,500,513,514,515,530,548,554,563,587,593,601,631,636,660,674,691,694,749,751,843,873,901,902,903,987,990,992,993,994,995,1000,1167,1234,1433,1434,1521,1528,1723,1812,1813,2000,2049,2375,2376,2077,2078,2082,2083,2086,2087,2095,2096,2222,2433,2483,2484,2638,3000,3260,3283,3306,3389,3478,3690,4000,5000,5432,5433,6000,6667,7000,8000,8080,8443,8880,8888,9000,9001,9418,9998,27017,27018,27019,28017,32400"

# periodically display runtime stats to STDERR, in seconds
runtime_stats = 0
runtime_stats_last_timestamp = 0
runtime_stats_last_port_count = 0

# initialize variables
active_hosts = defaultdict(list)
hosts_scanned = 0
skipped_hosts = 0
skipped_ports = 0
opened_ports = 0
ports_scanned = 0
skipped_port_list = []
resolve_dns = 0

#############################################################################################

def is_ip_on_lan(ip:str) -> bool:
	"""Return true when the given IP is in a IANA IPv4 private range, otherwise false

	Args:
		ip An IPv4 address in dotted-quad notation.

	Returns:
		true or false depending on the value of ip

	Raises:
		Does not raise any errors.
	"""
	return ipaddress.IPv4Address(ip).is_private

#############################################################################################

def get_port_list(ports:str) -> list:
	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		if end < start:
			print("\nError: For -p option, ending port is less than starting port\n")
			sys.exit(1)
		if end > 65535:
			print("\nError: For -p option, ending port is greater than 65535\n")
			sys.exit(1)
		port_list = list(range(start,end+1))
	else:
		# comma separated list of ports, can also include a single port
		port_list = ports.split(",")

	return port_list

#############################################################################################

def scan_one_host(ip: str, ports: str) -> None:
	"""Scan a host for the given open ports.
	
	Args:
		ip: An IPv4 address in dotted-quad notation.

		ports: A list of ports in either range format (x-y) or
		    list format (a,b,c,d).

	Returns:
		Does not return any values.

	Raises:
		Does not raise any errors.
	"""

	global args, max_workers, connect_timeout, hosts_scanned
	global connect_timeout_lan, connect_timeout_wan

	if ports.find("-") > -1 and ports.find(",") > -1:
		print("\nError: For -p option, port list cannot contain both a port range and list of ports\n")
		sys.exit(1)

	hosts_scanned += 1
	port_list = get_port_list(ports)

	# set the timeout based on lan or wan
	if not connect_timeout:
		connect_timeout = connect_timeout_lan if is_ip_on_lan(ip) else connect_timeout_wan

	if args.shuffleports: shuffle(port_list)
	with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
		alpha = {executor.submit(scan_one_port, ip, current_port): current_port for current_port in port_list}
		for future in concurrent.futures.as_completed(alpha):
			pass

#############################################################################################

def scan_one_port(ip: str, port:str) -> bool:
	"""Scan the given host for one open port.
	
	Args:
		ip: An IPv4 address in dotted-quad notation.

		port: A TCP port number 1-65535 (as a string).

	Returns:
		Returns True if the port is open and
		False otherwise.

	Raises:
		Does not raise any errors.
	"""

	global args, fp_output, active_hosts, opened_ports, ports_scanned
	global max_workers, connect_timeout_lan, connect_timeout_wan, skipped_port_list, skipped_ports, resolve_dns
	global runtime_stats, runtime_stats_last_timestamp, runtime_stats_last_port_count

	port = int(port)
	if port > 65535:
		print("\nError: Port is greater than 65535\n")
		return False

	if port in skipped_port_list:
		if args.verbose:
			line = "{}\t{}\tport-excluded".format(ip,port)
			print(line)
			if args.output: 
				fp_output.write("%s\n" % (line.replace("\t",",")))
				fp_output.flush()
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
			if resolve_dns:
				try:
					name = socket.gethostbyaddr(ip)
					name = name[0]
				except:
					name = ""
				line = "{}\t{}\topen\t{}".format(ip, port,name)
			else:
				line = "{}\t{}\topen".format(ip, port)
			print(line)
			if args.output: 
				fp_output.write("%s\n" % (line.replace("\t",",")))
				fp_output.flush()
		else:
			valid = False
			if args.closed: 
				line = "{}\t{}\tclosed".format(ip, port)
				print(line)
				if args.output: 
					fp_output.write("%s\n" % (line.replace("\t",",")))
					fp_output.flush()
			
		sock.close()
		if runtime_stats:
			now = int(time.time())
			if (now-runtime_stats_last_timestamp) >= runtime_stats:
				runtime_stats_last_timestamp = now
				pps = (ports_scanned-runtime_stats_last_port_count) / runtime_stats
				print("[%s]\thosts:%s\tports:%s\tports/sec:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),hosts_scanned,ports_scanned,int(pps)), file=sys.stderr)
				runtime_stats_last_port_count = ports_scanned

		return valid

	except KeyboardInterrupt:
		print("You pressed Ctrl+C")
		return False

	except socket.error:
		print("Couldn't connect to server %s on port %s" % (ip,port))
		return False

#############################################################################################

def create_skipped_port_list(ports:str) -> None:
	"""Create a Python list from the given argument string.
	
	Args:
		ports: A list of ports in either range format (x-y) or
		    list format (a,b,c,d).

	Returns:
		Modifies the global skipped_port_list, which is a Python
		list to include all ports that will be excluded from scanning.

	Raises:
		Does not raise any errors.
	"""

	global skipped_port_list 

	if ports.find("-") > 0 and ports.find(",") == -1:
		# hypen delimited range of ports
		start, end = ports.split("-")
		start = int(start)
		end = int(end)
		if end < start:
			print("\nError: For -X option, ending port is less than starting port\n")
			sys.exit(1)
		skipped_port_list = list(range(start,end+1))
	else:
		# comma separated list of ports, can also include a single port
		skipped_port_list = [int(n) for n in ports.split(",")]

#############################################################################################

def tcp_connect_handler(sock:socket.socket, remote:list, server:socketserver.TCPServer):
	now = time.strftime("%Y-%m-%d %H:%M:%S")
	print("[%s] Incoming connection on %s:%s from %s:%s" % (now,sock.getsockname()[0],sock.getsockname()[1],remote[0],remote[1]))
	#sock.shutdown(socket.SHUT_RDWR)
	sock.close()

#############################################################################################

def tcp_listen(port:int) -> None:
	host = "0.0.0.0"

	print("Listening for incoming TCP connections on %s:%s" % (host,port))
	print("Press Ctrl-Break to exit.")
	server = socketserver.TCPServer((host, port), tcp_connect_handler)
	server.serve_forever()

#############################################################################################

def tcp_listen_setup(ports:str) -> None:
	port_list = get_port_list(ports)

	with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
		alpha = {executor.submit(tcp_listen, int(current_port)): current_port for current_port in port_list}
		for future in concurrent.futures.as_completed(alpha):
			pass

#############################################################################################

def main() -> None:
	"""Process command-line arguments, scan hosts/ports, print results.
	
	Args:
		None

	Returns:
		None

	Raises:
		Does not raise any errors.
	"""

	global args, fp_output, default_port_list
	global max_workers, connect_timeout, connect_timeout_lan, connect_timeout_wan
	global skipped_hosts, skipped_ports, hosts_scanned
	global resolve_dns, runtime_stats, runtime_stats_last_timestamp

	parser = argparse.ArgumentParser(description="tcpscan.py: a simple, multi-threaded IPv4 TCP port scanner", epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("target", help="e.g. 192.168.1.0/24 192.168.1.100 www.example.com")
	parser.add_argument("-x", "--skipnetblock", help="skip a sub-netblock, e.g. 192.168.1.96/28")
	parser.add_argument("-X", "--skipports", help="exclude a subset of ports, e.g. 135-139")
	parser.add_argument("-p", "--ports", help="comma separated list or hyphenated range, e.g. 22,80,443,445,515  e.g. 80-515")
	parser.add_argument("-T", "--threads", help="number of concurrent threads, default: %s" % (max_workers))
	parser.add_argument("-t", "--timeout", help="number of seconds to wait for a connect, default: %s for lan, %s for wan" % (connect_timeout_lan,connect_timeout_wan))
	parser.add_argument("-s", "--shufflehosts", help="randomize the order IPs are scanned", action="store_true")
	parser.add_argument("-S", "--shuffleports", help="randomize the order ports are scanned", action="store_true")
	parser.add_argument("-c", "--closed", help="output ports that are closed", action="store_true")
	parser.add_argument("-o", "--output", help="output to CSV file")
	parser.add_argument("-d", "--dns", help="revolve IPs to dns names", action="store_true")
	parser.add_argument("-v", "--verbose", help="output statistics", action="store_true")
	parser.add_argument("-r", "--runtime", help="periodically display runtime stats every RUNTIME seconds to STDERR")
	parser.add_argument("-l", "--loop", help="repeat the port scan LOOP times, 0 for continuous")
	parser.add_argument("-L", "--listen", help="listen on given TCP port(s) for incoming connection(s) [mutually exclusive]", action="store_true")


	args = parser.parse_args()

	if args.listen:
		try:
			tcp_listen_setup(args.target)
		except:
			print("Done")
			sys.exit(0)
		finally:
			sys.exit(0)
	
	if "." == args.target:
		args.target = "127.0.0.1"
	if args.threads:
		max_workers = int(args.threads)
	if args.timeout:
		connect_timeout = float(args.timeout)
	if args.output:
		fp_output = open(args.output,mode="w",encoding="latin-1")
	if args.skipports:
		create_skipped_port_list(args.skipports)
	if args.runtime:
		runtime_stats = int(args.runtime)
		runtime_stats_last_timestamp = int(time.time())

	loop_seconds = int(args.loop) if args.loop else 1
	if 0 == loop_seconds:
			loop_seconds = int(sys.maxsize) - 1
	
	port_list = args.ports if args.ports else default_port_list
	ip_skiplist = ipaddress.ip_network(args.skipnetblock) if args.skipnetblock else []

	if any(c.isalpha() for c in args.target):
		try:
			ip = socket.gethostbyname(args.target)
			hosts = (ip,)
		except:
			print("Unable to resolve hostname:", args.target)
			sys.exit(1)
	else:
		try:
			tmp = ipaddress.ip_network(args.target)
		except ValueError as err:
			print("Error:", err)
			sys.exit(1)

		hosts = list(tmp.hosts())
		if args.shufflehosts:
			shuffle(hosts)
		
		if not len(hosts): # a single ip-address was given on cmd-line
			tmp = args.target.replace("/32","")
			hosts = (tmp,)
	
	if args.dns:
		resolve_dns = True

	t1 = datetime.now()
	for loop in range(0,loop_seconds):
		for tmp in hosts:
			my_ip = "%s" % (tmp)
			if tmp in ip_skiplist:
				if args.verbose:
					line = "{}\tn/a\thost-excluded".format(my_ip)
					print(line)
					if args.output: 
						fp_output.write("%s\n" % (line.replace("\t",",")))
						fp_output.flush()
				skipped_hosts += 1
				continue
			try:
				scan_one_host( "%s" % (my_ip), port_list )
			except KeyboardInterrupt:
				print("\nYou pressed Ctrl+C")
				break

		if loop_seconds and args.loop:
			try:
				print("[%s] completed loops:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"), loop+1))
				print()
				time.sleep(0.70)
			except KeyboardInterrupt:
				print("\nYou pressed Ctrl+C")
				break

	if runtime_stats:
		now = int(time.time())
		divisor = now - runtime_stats_last_timestamp
		if not divisor: divisor=1
		pps = (ports_scanned-runtime_stats_last_port_count) / divisor
		print("[%s]\thosts: %s\tports: %s\tports/sec: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"),hosts_scanned,ports_scanned,int(pps)), file=sys.stderr)

	if args.verbose:
		print()
		print("Scan Time      : ", datetime.now() - t1)
		print("Active Hosts   : ", len(active_hosts))
		print("Hosts Scanned  : ", hosts_scanned)
		print("Skipped Hosts  : ", skipped_hosts)
		print("Opened Ports   : ", opened_ports)
		print("Skipped Ports  : ", skipped_ports)
		print("Ports Scanned  : ", ports_scanned)
		print("Completed Loops: ", loop+1)
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

