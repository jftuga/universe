#!/usr/bin/env python3

"""
ipinfo.py

Query https://ipinfo.io for IP address info including geographic location when given IP address, host name or URL
Multiple arguments can be given on cmd line

Example:
ipinfo.py uga.edu gatech.edu clemson.edu sc.edu utk.edu auburn.edu unc.edu www.uky.edu ufl.edu olemiss.edu www.virginia.edu louisiana.edu umiami.edu missouri.edu utexas.edu texastech.edu

MIT License; Copyright (c) 2018 John Taylor
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import concurrent.futures
import geopy.distance
import json
import re
import socket
import sys
import time
import urllib.request
from collections import defaultdict
from veryprettytablepatched import VeryPrettyTablePatched

pgm_version = "2.1"

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

    return (obj, n[2])

##########################################################################

def get_ip_info(ip:str, hostname:str) -> str:
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
    info = json.loads(text)
    info["input"] = hostname
    return info

##########################################################################

def str2tup(loc:str) -> tuple:
    a,b = loc.split(",")
    return ( float(a), float(b) )

##########################################################################

def build_row(obj:str, my_loc:str) -> tuple:
    result = []
    all_keys = ( "input", "ip", "hostname", "org", "loc", "city", "region", "country" )
    for key in all_keys:
        if key in obj:
            result.append(obj[key])
        else:
            result.append("")

    if "loc" in all_keys:
        try:
            distance = "%.2f" % (geopy.distance.vincenty(str2tup(my_loc), str2tup(obj["loc"])).mi)
            result.append(distance)
        except:
            result.append("")
    else:
        result.append("")

    return tuple(result)

##########################################################################

def get_my_coords() -> str:
    url = "https://ipinfo.io/json"
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
    
    obj = json.loads(text)
    return obj["loc"]

##########################################################################

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("%s: [ IP address | host name | URL ] ..." % (sys.argv[0]))
        print()
        return
    
    # max number of concurrent web requests
    max_workers = 30

    ip_re = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    my_loc = get_my_coords()

    tbl = VeryPrettyTablePatched()
    tbl.field_names = ( "input", "ip", "hostname", "org", "loc", "city", "region", "country", "distance (mi)" )
    tbl.align = "l"

    host_ip_list = []
    host_ip_tbl = defaultdict(list)

    for obj in sys.argv[1:]:
        if obj.find("://") > 1:
            host_name = obj.split("/")[2]
            host_ip_list.append( host_name )
            obj = host_name
        else:
            match = ip_re.findall(obj)

            if len(match):
                host_ip_list.append(match[0])
            else:
                host_ip_list.append(obj)

    # host_ip_list is a list containing either a host name with the URL stripped or an IP address (1 per cmd-line argument)
    #print( host_ip_list )

    with concurrent.futures.ThreadPoolExecutor(max_workers,thread_name_prefix="resolve") as executor:
        dns_result = {executor.submit(resolve,host): host for host in host_ip_list}
        for future in concurrent.futures.as_completed(dns_result):
            if future.done():
                fu_res = future.result()
                for ip in fu_res[1]:
                    host_ip_tbl[ip] = fu_res[0]

    # host_ip_tbl is a dict with key=ip, value=hostname or IP address
    # the same value can be used by multiple distinct keys
    #for ip in host_ip_tbl:
    #    print(ip, host_ip_tbl[h])

    with concurrent.futures.ThreadPoolExecutor(max_workers,thread_name_prefix="get_ip_info") as executor:
        json_result = {executor.submit(get_ip_info,ip,host_ip_tbl[ip]): ip for ip in host_ip_tbl}
        for future in concurrent.futures.as_completed(json_result):
            if future.done():
                ip_table = future.result()
                tbl.add_row(build_row(ip_table,my_loc))

    print( tbl.get_string(sortby="input"))

##########################################################################

if __name__ == '__main__':
    time_start = time.time()
    main()
    time_end = time.time()
    print()
    print("elapsed time: %.2f seconds" % (time_end - time_start) )

