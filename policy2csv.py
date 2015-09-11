
import re

input="policy.txt"

stanza_re = re.compile("edit ([0-9]+.*?    )next",re.M|re.I|re.S)

srcint_re = re.compile('set srcintf "(.*?)"')
dstint_re = re.compile('set dstintf "(.*?)"')

srcaddr_re = re.compile('set srcaddr (".*")')
dstaddr_re = re.compile('set dstaddr (".*")')

svc_re = re.compile('set service (".*")')

comments_re = re.compile('set comments (".*")')

action_re = re.compile('set action (.*?)\n')

policy = file(input).read()

rule_set = stanza_re.findall(policy)


print "Interfaces\tSources\tDestinations\tServices\tAction\tRule #\tComments"
for rule in rule_set:
	pos = rule.find("\n")
	rule_num = rule[:pos]
	rule_num = int(rule_num)

	tmp = srcint_re.findall(rule)
	srcint = tmp[0]

	tmp = dstint_re.findall(rule)
	dstint = tmp[0]

	srcint = srcint.replace("port1","isa-dmz").replace("port2","web-dmz").replace("port4","email-dmz").replace("wan1","internal").replace("wan2","external")
	dstint = dstint.replace("port1","isa-dmz").replace("port2","web-dmz").replace("port4","email-dmz").replace("wan1","internal").replace("wan2","external")

	tmp = srcaddr_re.findall(rule)
	slots = tmp[0].split('"')
	if 3 == len(slots):
		srcaddr = slots[1].replace('"','')
	else:
		srcaddr = '"' + slots[1]
		for i in range(3,len(slots),2):
			srcaddr += "\n" + slots[i]
		srcaddr += '"'

	tmp = dstaddr_re.findall(rule)
	slots = tmp[0].split('"')
	if 3 == len(slots):
		dstaddr = slots[1].replace('"','')
	else:
		dstaddr = '"' + slots[1]
		for i in range(3,len(slots),2):
			dstaddr += "\n" + slots[i]
		dstaddr += '"'
	
	tmp = svc_re.findall(rule)
	svc = tmp[0].replace('"',',')
	svc = svc[1:-1]
	svc = svc.replace(", ,",",")

	tmp = comments_re.findall(rule)
	if len(tmp):
		comments = tmp[0].replace('"','')
	else:
		comments = ""

	tmp = action_re.findall(rule)
	if len(tmp):
		action = tmp[0]
	else:
		action = ""


	if 0:
		print rule_num
		print srcint + " -->> " +  dstint
		print srcaddr + " -> " + dstaddr
		print svc
		print "=" * 77

	print "%s:%s\t%s\t%s\t%s\t%s\t%s\t%s" % (srcint,dstint,srcaddr,dstaddr,svc,action,rule_num,comments)
	

