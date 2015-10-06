#!/usr/bin/env python3

"""
change_dhcp_scope.py
-John Taylor
Oct-06-2015

Change the dhcp scope and netmask in a Windows Server DHCP file exported by:
netsh dhcp server \\%SVR% scope %SCOPE% dump > exported.txt

See also: https://stackoverflow.com/questions/32974191/string-replacement-using-python-3-re-sub
          http://social.technet.microsoft.com/wiki/contents/articles/8484.how-to-easily-change-a-dhcp-s-scope-subnet.aspx
"""

import sys, re, argparse

def change_netmask(nm,data):
	netmask_pattern = r'(Dhcp Server .*? add scope [\d.]+) [\d.]+ (.*)'
	netmask_repl = r"\1 %s \2" % (nm)
	return re.sub(netmask_pattern,netmask_repl,data)

def change_scope(old,new,data):
	scope_repl = r"\1 %s \2" % (new)

	# no colon, no comma
	scope1_pattern = r'(Dhcp Server .*? Scope) %s (.*)' % (old)
	tmp1 = re.sub(scope1_pattern,scope_repl,data,count=0,flags=re.I)
	
	# include colon, no comma
	scope2_pattern = r'(#.*? Scope :) %s(.*)' % (old)
	tmp2 = re.sub(scope2_pattern,scope_repl,tmp1,count=0,flags=re.I)

	# no colon, include comma
	scope3_pattern = r'(#.*? Scope )%s(,.*)' % (old)
	return re.sub(scope3_pattern,scope_repl,tmp2,count=0,flags=re.I)

def remove_header(data):
	pattern= r'Changed the current scope context to .*'
	return re.sub(pattern,"",data)

def main():
	parser = argparse.ArgumentParser(description="Change DHCP Scope")
	parser.add_argument("fname", help="Exported DHCP filename")
	parser.add_argument("oldscope", help="Old scope name (ex: 10.0.1.0)")
	parser.add_argument("newscope", help="New scope name (ex: 10.0.0.0)")
	parser.add_argument("netmask", help="New scope netmask (ex: 255.255.254.0)")

	args = parser.parse_args()
	data = open(args.fname,mode="r",encoding="latin-1").read()
	
	tmp1 = change_netmask(args.netmask,data)
	tmp2 = change_scope(args.oldscope,args.newscope,tmp1)
	tmp3 = remove_header(tmp2)
	print(tmp3)

	return 0

if "__main__" == __name__:
	sys.exit( main() )
