#!/usr/bin/env python3

"""
ipinfo.py

Query https://ipinfo.io for IP address info including geographic location when given IP address, host name or URL
Multiple arguments can be given on cmd line

Example:
ipinfo uga.edu gatech.edu clemson.edu sc.edu utk.edu auburn.edu unc.edu www.uky.edu ufl.edu olemiss.edu www.virginia.edu louisiana.edu umiami.edu missouri.edu utexas.edu texastech.edu

MIT License; Copyright (c) 2018 John Taylor
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import concurrent.futures
import json
import math
import re
import socket
import sys
import time
import urllib.request
from collections import defaultdict
from veryprettytablepatched import VeryPrettyTablePatched

pgm_version = "2.2"

# constants for vincenty()
# WGS 84
a = 6378137  # meters
f = 1 / 298.257223563
b = 6356752.314245  # meters; b = (1 - f)a
MILES_PER_KILOMETER = 0.621371
MAX_ITERATIONS = 200
CONVERGENCE_THRESHOLD = 1e-12  # .000,000,000,001

##########################################################################

# adapted from: https://pypi.python.org/pypi/vincenty/
def vincenty(point1, point2, miles=True):

    # short-circuit coincident points
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return 0.0

    U1 = math.atan((1 - f) * math.tan(math.radians(point1[0])))
    U2 = math.atan((1 - f) * math.tan(math.radians(point2[0])))
    L = math.radians(point2[1] - point1[1])
    Lambda = L

    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)

    for iteration in range(MAX_ITERATIONS):
        sinLambda = math.sin(Lambda)
        cosLambda = math.cos(Lambda)
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 +
                             (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        try:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        except ZeroDivisionError:
            cos2SigmaM = 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LambdaPrev = Lambda
        Lambda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                               (cos2SigmaM + C * cosSigma *
                                                (-1 + 2 * cos2SigmaM ** 2)))
        if abs(Lambda - LambdaPrev) < CONVERGENCE_THRESHOLD:
            break  # successful convergence
    else:
        return None  # failure to converge

    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma *
                 (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM *
                 (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)

    s /= 1000  # meters to kilometers
    if miles:
        s *= MILES_PER_KILOMETER  # kilometers to miles

    return round(s, 6)

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
            distance = "%.2f" % (vincenty(str2tup(my_loc), str2tup(obj["loc"]),miles=True))
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

    print( tbl.get_string(sortby="distance (mi)"))

##########################################################################

if __name__ == '__main__':
    time_start = time.time()
    main()
    time_end = time.time()
    print()
    print("elapsed time: %.2f seconds" % (time_end - time_start) )

