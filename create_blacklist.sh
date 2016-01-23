#!/bin/bash

# create_blacklist.sh
# Jan-23-2016
#
# Create an unbound bad_hosts file to block ads
#

REWT="/tmp/blacklist"
UNBOUND_SRC="${REWT}/bad_hosts"
UNBOUND_DST="/etc/unbound/bad_hosts"
AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"

SOURCES=('https://adaway.org/hosts.txt'
'http://adblock.gjtech.net/?format=unix-hosts'
'http://hosts-file.net/ad_servers.txt'
'http://www.malwaredomainlist.com/hostslist/hosts.txt'
'http://someonewhocares.org/hosts/hosts'
'http://winhelp2002.mvps.org/hosts.txt'
'http://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext')

function get_source() {
	src_url=$1
	src_num=$2
	
	fname="${REWT}/${src_num}.txt"	
	if [ ! -e "${fname}" ] ; then
		wget --user-agent="${AGENT}" -O ${fname} ${src_url}
	fi
}

function clean_source() {
	src_num=$1
	fname="${REWT}/${src_num}.txt"
	output="${REWT}/${src_num}.hosts.txt"
	if [ ! -e "${output}" ] ; then
		egrep -v "^::|localhost|localdomain$|^255.255.255.255|local$|^#|^$" ${fname} | sed -e "s/0\.0\.0\.0/127.0.0.1/" | awk 'length($0) > 9 {print $1,$2}' > ${output}
	fi
}

function merge_for_unbound() {
	echo
	echo "Merging sources for unbound..."
	echo
	cat ${REWT}/*.hosts.txt | sort | uniq | remove_linefeed.py | grep -v "#" | awk '{print "local-data: \""$2" A "$1"\""}' > ${UNBOUND_SRC}
}

function install_new_version() {
	echo
	echo "Installing new unbound bad_hosts file..."
	echo
	archive=bad_hosts--`date +"%Y%m%d.%H%M%S"`
	mv ${UNBOUND_DST} ${archive}
	xz -v ${archive}
	mv ${UNBOUND_SRC} ${UNBOUND_DST}
	service unbound restart
}

function main() {
	mkdir ${REWT} > /dev/null 2>&1
	#rm ${REWT}/*.txt > /dev/null 2>&1
	
	for ((i = 0; i < "${#SOURCES[@]}"; i++))
	do
		url=${SOURCES[$i]}
		echo "${i} ${url}"
		get_source ${url} ${i}
		clean_source ${i}
	done
	
	merge_for_unbound
	install_new_version
}

main
