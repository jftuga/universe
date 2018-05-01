#!/usr/bin/env python3

"""
udplogger.py 
-John Taylor

A simple, multi-threaded, cross-platform IPv4 UDP port listener/logger for Python 3.5

examples
--------
1) python3 udplogger.py -h
     (help, shows all options)

2) python3 udplogger.py 53,67,68,137
    (concurrently listen on these 4 UDP ports)

3) python3 udplogger.py -d -o results.csv 53,67,68,137
    (same as example 2, but also resolve DNS and log connections to results.csv)

MIT License Copyright (c) 2018 John Taylor
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

To build a windows executable:
pyinstaller -F --noupx udplogger.py

"""

import os.path
import sys
import socket
import socketserver
import argparse
import time
import concurrent.futures

pgm_version = "1.01"

# CSV logger for --output
fp_udp_listen = False

# save DNS lookups into a dict where key=ip, val=hostname
dns_cache = {}

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

def udp_connect_handler(sock:socket.socket, remote:list, server:socketserver.UDPServer):
    global dns_cache

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    remote_addr = remote[0]

    if resolve_dns:
        if remote_addr not in dns_cache:
            remote_addr_info = []
            try:
                remote_addr_info = socket.gethostbyaddr(remote_addr)
            except socket.herror:
                pass
            except:
                msg = "\n%s\n%s\n" % (sys.exc_info()[0],sys.exc_info()[1])
                print(msg)

            if len(remote_addr_info) >= 1:
                remote_addr = remote_addr_info[0]
                dns_cache[remote[0]] = remote_addr
        else:
            remote_addr = dns_cache[remote_addr]

    print("[%s] Incoming connection on %s:%s from %s:%s" % (now,sock[1].getsockname()[0],sock[1].getsockname()[1],remote_addr,remote[1]))
    
    if fp_udp_listen:
        fp_udp_listen.write("%s,%s:%s,%s:%s\n" % (now,sock[1].getsockname()[0],sock[1].getsockname()[1],remote_addr,remote[1]))
        fp_udp_listen.flush()

#############################################################################################

def udp_listen(port:int) -> None:
    """Listen on one specific UDP port

    Args:
        port: the UDP port to listen on
    """
    host = "0.0.0.0"

    print("Listening for incoming UDP connections on %s:%s" % (host,port))
    server = socketserver.UDPServer((host, port), udp_connect_handler)
    server.serve_forever()

#############################################################################################

def udp_listen_setup(ports:str, output:str) -> None:
    """Listen for incoming connection on a group of ports and log them to a CSV file

       Args:
            ports: a list of ports, such as 80,443,8080 or 20-25

            output: (optional) a CSV file name
    """
    global fp_udp_listen

    if output and not os.path.exists(output):
        fp_udp_listen = open(output,mode="w",encoding="latin-1")
        fp_udp_listen.write("Timestamp,Local,Remote\n")
        fp_udp_listen.flush()
    elif output:
        fp_udp_listen = open(output,mode="a",encoding="latin-1")

    port_list = get_port_list(ports)
    print("\nPress Ctrl-C, Ctrl-\\ or Ctrl-Break to exit.\n")
    max_workers = len(port_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        alpha = {executor.submit(udp_listen, int(current_port)): current_port for current_port in port_list}
        for future in concurrent.futures.as_completed(alpha):
            pass

#############################################################################################

def main() -> None:
    """Process command-line arguments, set up UDP listeners.
    
    Args:
        None

    Returns:
        None
    """
    global args, resolve_dns

    parser = argparse.ArgumentParser(description="udplogger: A multi-threaded, cross-platform IPv4 UDP port listener/logger", epilog="udplogger version: %s" % (pgm_version))
    parser.add_argument("ports", help="comma separated list or hyphenated range, e.g. 53,67,68,123,137,138  e.g. 53-1000")
    parser.add_argument("-o", "--output", help="output to CSV file")
    parser.add_argument("-d", "--dns", help="resolve IPs to host names", action="store_true")

    args = parser.parse_args()
    resolve_dns = True if args.dns else False

    try:
        udp_listen_setup(args.ports,args.output)
    except:
        msg = "\n%s\n%s\n" % (sys.exc_info()[0],sys.exc_info()[1])
        print(msg)
        sys.exit(1)
    finally:
        sys.exit(0)

    if args.output:
        fp_output.close()

#############################################################################################

if "__main__" == __name__:
    main()
