#!/bin/bash

# ubnt-hole.sh
# -John Taylor
# May-4-2016

# This is inspired by https://pi-hole.net/ It is used on a Ubiquity
# EdgeRouter Lite in conjunction with unbound DNS server.  The version
# of Unbound that ships with the router is buggy and Unbound will
# crash every few days.  I recommend upgrading to version 1.4.22, which
# you will need to compile from source: apt-get install build-essential 
# to install gcc, make, etc.

# example cron entry:
# 02 15 * * * /root/ubnt-hole/create_bad_hosts_file.sh > /root/ubnt-hole/create_bad_hosts.log 2>&1

# example unbound.conf:
# change the interface and access-control lines for your internal IPs
# server:
#     verbosity: 1
#     include: "/etc/unbound/bad_hosts"
#     include: "/etc/unbound/lan_hosts"
#     statistics-interval: 3600
#     interface: 192.168.1.2
#     outgoing-interface: 192.168.1.2
#     access-control: 127.0.0.0/8 allow
#     access-control: 192.168.1.0/24 allow
#     logfile: "/var/log/unbound.log"
#     log-time-ascii: yes

# whitelist.txt:
# contains a list of good/safe dns names, one per line
# blacklist.txt:
# contains a list of bad/undesirable dns names (not included by what is downloaded), one per line
# lan_hosts:
# contains dns for your local subnet, one entry per line, format:
# local-data: "mydesktop.pri A 192.168.1.3"


WORK="work"
CLEAN="${WORK}/cleaned.txt"
FINAL="${WORK}/bad_hosts"
TARGET="/etc/unbound"
WHITELIST="${TARGET}/whitelist.txt"
BLACKLIST="${TARGET}/blacklist.txt"

if [ ! -d ${WORK} ] ; then
    mkdir -m700 ${WORK}
fi
rm -f ${CLEAN} ${FINAL} ${WORK}/ad_*.txt


echo
echo Downloading...
echo

wget -O ${WORK}/ad_1.txt "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
wget -O ${WORK}/ad_2.txt "http://adblock.gjtech.net/?format=unix-hosts"
wget -O ${WORK}/ad_3.txt "http://mirror1.malwaredomains.com/files/justdomains"
wget -O ${WORK}/ad_4.txt "http://sysctl.org/cameleon/hosts"
wget -O ${WORK}/ad_5.txt "http://zeustracker.abuse.ch/blocklist.php?download=domainblocklist"
wget -O ${WORK}/ad_6.txt "https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt"
wget -O ${WORK}/ad_7.txt "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt"
wget -O ${WORK}/ad_8.txt "http://hosts-file.net/ad_servers.txt"
wget -O ${WORK}/ad_9.txt "https://raw.githubusercontent.com/quidsup/notrack/master/trackers.txt"


echo
echo Clean and consolidate...
echo
cat ${WORK}/ad_*.txt | sed -e 's/0\.0\.0\.0 //g' -e 's/127\.0\.0\.1//g' -e 's/#.*//' -e 's/\r//g' | grep -v ^# | grep -v ^$ | tr '[A-Z]' '[a-z]' | sort | uniq > ${CLEAN}


echo
echo Convert to unbound format...
echo

if [ -e ${WHITELIST} ] ; then
    cat ${CLEAN} | grep -v -f ${WHITELIST} | mawk '{ printf("local-data: %c%s A 127.0.0.1%c\n",34,$1,34) }' | sort | uniq > ${FINAL}
else
    cat ${CLEAN} | mawk '{ printf("local-data: %c%s A 127.0.0.1%c\n",34,$1,34) }' | sort | uniq > ${FINAL}
fi

if [ -e ${BLACKLIST} ] ; then
    cat ${BLACKLIST} | mawk '{ printf("local-data: %c%s A 127.0.0.1%c\n",34,$1,34) }' >> ${FINAL}
fi


echo
echo Archive old version...
echo

CURR="${TARGET}/bad_hosts"
NOW=`date +"%Y%m%d.%H%M%S"`
if [ -e "${CURR}" ] ; then
    mv ${CURR} ${CURR}--${NOW}
    xz -v ${CURR}--${NOW}
fi


echo
echo Install and restart...
echo
cp ${FINAL} ${TARGET}
/sbin/unbound-control stop
sync ; sleep 1 ; sync
export PATH="/sbin:/usr/local/sbin:${PATH}"
/sbin/unbound-control start

