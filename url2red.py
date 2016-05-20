#!/usr/bin/env python3

"""
url2red.py
Sep-9-2015
-John Taylor

transform URLs into reddit Markdown by downloading the given URLs and extracting their titles

Example:
./url2red.py https://www.youtube.com/watch?v=75XeVyeq8GY https://www.youtube.com/watch?v=awlyr6AFGyA
"""

import sys,urllib.request,re,time,html
title_re = re.compile("<title>(.*?)</title>",re.M|re.S)

def main():
	if len(sys.argv) < 2:
		print(); print("Usage: %s [youtube-url] [youtube-url] ..." % (sys.argv[0])); print()
		return 1

	print()
	for url in sys.argv[1:]:
		response = urllib.request.urlopen(url)
		data = response.read()
		text = data.decode('utf-8')

		matches = title_re.findall(text)
		if not matches:
			print(); print("Error: Unable to find title when using the 'title_re' regular expression."); print()
			return 1

		url = url.replace(")","\\)")
		title = matches[0]
		title=html.unescape(title)
		#title = title.replace(" - YouTube","")
		#title = title.replace(" - Wikipedia, the free encyclopedia","")
		title = title.replace("[","(").replace("]",")").strip()
		title = re.sub(' - (.*?)$','',title)
		title = re.sub(' \| (.*?)$','',title)
		title = re.sub(' +',' ', title)
		reddit = "[%s](%s)" % (title,url)
		print(reddit)
		if len(sys.argv) > 2: time.sleep(0.33)
	
	print()
	return 0

if __name__ == "__main__":
	sys.exit( main() )

