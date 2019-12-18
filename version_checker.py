#!/usr/bin/env python3

import concurrent.futures
import re
import sys
import urllib.request
from collections import defaultdict

software = defaultdict(dict)

"""
403 Errors

#software["Git"]["url"] = "https://git-scm.com/download/win"
#software["Git"]["match"] = re.compile("downloading the latest.*?<strong>(.*?)</strong>",re.I|re.M|re.S)
#software["Git"]["url"] = "https://gitforwindows.org/"
#software["Git"]["match"] = re.compile("<span class="version">(.*?)</",re.I|re.M|re.S)
"""

if 1:
    software["PHP 7.3"]["url"] = "https://windows.php.net/download/"
    software["PHP 7.3"]["match"] = re.compile("""id="php-7.3".*?class=.*?>.*? \((.*?)\)</""",re.I|re.M|re.S)

    software["Python 3.8"]["url"] = "https://www.python.org/downloads/windows/"
    software["Python 3.8"]["match"] = re.compile(""">Stable Releases<.*?href="/downloads/release/python-38.*?>Python (3.8.*?) """,re.I|re.M|re.S)

    software["Go 1.13"]["url"] = "https://golang.org/dl/"
    software["Go 1.13"]["match"] = re.compile(""">Stable versions<.*?class="download" href="https://dl.google.com/go/go(1.13.*?).src.tar.gz""",re.I|re.M|re.S)

    software["Rust 1"]["url"] = "https://www.rust-lang.org/"
    software["Rust 1"]["match"] = re.compile("""class="download-link">Version (.*?)<""",re.I|re.M|re.S)

    software["Aria2c"]["url"] = "https://aria2.github.io/"
    software["Aria2c"]["match"] = re.compile("""Download <a href="https://github.com/aria2/aria2/releases/tag.*?>version (.*?)<""",re.I|re.M|re.S)

    software["FSCapture"]["url"] = "https://www.faststone.org/FSCaptureDetail.htm"
    software["FSCapture"]["match"] = re.compile("""(?=Version).*?(\d+\.\d+)""",re.I|re.M|re.S)

    software["Putty"]["url"] = "https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html"
    software["Putty"]["match"] = re.compile("""<h1.*?latest release \((.*?)\)<""",re.I|re.M|re.S)

    software["Chrome"]["url"] = "https://www.whatismybrowser.com/guides/the-latest-version/chrome"
    software["Chrome"]["match"] = re.compile("""Chrome on <strong>Windows</strong>.*?<td>(.*?)</td>""",re.I|re.M|re.S)

    software["WinSCP"]["url"] = "https://winscp.net/eng/download.php"
    software["WinSCP"]["match"] = re.compile("""<h1>WinSCP (.*?) Download</h1>""",re.I|re.M|re.S)

    software["Java"]["url"] = "https://www.java.com/en/download/"
    software["Java"]["match"] = re.compile("""<h4.*?>.*?Version (.*?)....</""",re.I|re.M|re.S)

def safe_print(data,isError=False):
    dest = sys.stdout if not isError else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest )


def url_retrieve(url:str) -> str:
    try:
        response = urllib.request.urlopen(url)
    except:
        return ""
    data = response.read()
    reply = str(data)
    #with open("test.htm","w") as fp: fp.write("%s\n" % str(reply))
    return reply


def version_check(sw:dict,name:str):
    url = sw["url"]
    text = url_retrieve(url)

    match = sw["match"].findall(text)
    if not match:
        return "%12s: N/A - regexpr missed" % (name)
    #all_matches = ",".join(match)
    return "%12s: %s" % (name,match[0])

def test_one():
    name="FSCapture"
    v = version_check(software[name],name)
    print("v:",v)

def test_two():
    with open("test.htm") as fp: data = fp.read()
    
    version_re = re.compile("""(?=Version).*?(\d+\.\d+)""",re.I|re.M|re.S)
    #version_re = re.compile("\d\.\d(?<=Version.*?\d.\d)",re.I|re.M|re.S)
    match = version_re.findall(data)
    if match:
        print(match[0])
    else:
        print("no match")

def main():
    with concurrent.futures.ThreadPoolExecutor(len(software)) as executor:
        result = {executor.submit(version_check,software[name],name): name for name in software.keys()}
        for future in concurrent.futures.as_completed(result):
            if future.done():
                safe_print(future.result())


main()

# end of script    

