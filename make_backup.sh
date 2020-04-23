#!/bin/bash

# location of backups
BASE="/data/backups"

# what to back up
FOLDERS="etc home root var/lib/docker"

NOW=`date +%Y%m%d.%H%M%S`
DIR="${BASE}/backup--${NOW}"
PKG="${DIR}/installed_packages.txt"
FILES="${DIR}/all_files.txt"
ARCHIVE="${DIR}/${HOSTNAME}--${NOW}.tar"
LOG="${DIR}/status.log"

umask 077
if [ ! -e ${BASE} ] ; then
	mkdir -m 0700 ${BASE}
fi
mkdir ${DIR}

# create a list of user installed packages
zgrep -hE '^(Start-Date:|Commandline:)' $(ls -tr /var/log/apt/history.log* ) | egrep -v 'aptdaemon|upgrade' | egrep -B1 '^Commandline:' >| ${PKG}

# Side note:
# On CentOS systems use:
# yum history info 1 ; yum history info 2; etc...
# also to uninstall a large package with many dependencies: yum history undo 3 (for example)

# create a file system list
# https://github.com/jftuga/fstat
#find / 2> /dev/null | fstat -er '/sys/|^/proc/|^/run/|^/dev/' -sn -t 2> ${LOG} | xz -9 - > ${FILES}.xz &

# create a backup archive
cd / && tar -c -v '--exclude=.cache/*' -f ${ARCHIVE} ${FOLDERS} >> ${LOG} 2>&1
ls -l ${ARCHIVE} >> ${LOG}

# use this when not on a Raspberry Pi
#THREADS=`grep -c '^processor' /proc/cpuinfo`
THREADS=4

xz -6 -T${THREADS} ${ARCHIVE} >> ${LOG}
ls -l ${ARCHIVE}.xz >> ${LOG}


