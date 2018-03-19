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

import geopy.distance
import json
import re
import socket
import sys
import time
import urllib.request
from veryprettytablepatched import VeryPrettyTablePatched

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

def get_ip_info(ip:str) -> str:
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
    return json.loads(text)

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

def build_tbl(tbl:VeryPrettyTablePatched, obj:str):
    tbl.add_row(obj)

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

    ip_re = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    my_loc = get_my_coords()

    tbl = VeryPrettyTablePatched()
    tbl.field_names = ( "input", "ip", "hostname", "org", "loc", "city", "region", "country", "distance (mi)" )
    tbl.align = "l"

    for obj in sys.argv[1:]:
        if obj.find("://") > 1:
            host_name = obj.split("/")[2]
            host_ip_list = resolve( host_name )
            obj = host_name
        else:
            match = ip_re.findall(obj)

            if len(match):
                host_ip_list = match
            else:
                host_ip_list = resolve( obj )

        for ip in host_ip_list:
            json_result = get_ip_info(ip)
            json_result["input"] = obj
            tbl.add_row(build_row(json_result,my_loc))

            if(len(host_ip_list) > 1):
                time.sleep(0.25)

    print( tbl.get_string())

##########################################################################

if __name__ == '__main__':
    main()

