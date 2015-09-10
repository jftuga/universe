#!/bin/sh

LIST='/root/hacker_list.txt'

echo > ${LIST}
chmod 600 ${LIST}
echo "# created on `date`" >> ${LIST}
echo "# to show entries: pfctl -t hackers -T show" >> ${LIST}
echo >> ${LIST}

tcpdump -n -e -ttt -s 160 -r /var/log/pflog | awk '{print $10}' | cut -d. -f1-4 | sort -n | uniq  >> ${LIST}
pfctl -t hackers -T replace -f ${LIST}

# to view the log file:
# tcpdump -n -e -ttt -s 160 -r /var/log/pflog
#
# to vies PF table entries:
# pfctl -t hackers -T show
#
# to reset the hacker list:
# cat /dev/null > /var/log/pflog
# ps auxww | grep pflogd | grep /var/log | awk '{print $2}' | xargs kill -HUP

# (wait 1 minute for this cron job to take effect)
