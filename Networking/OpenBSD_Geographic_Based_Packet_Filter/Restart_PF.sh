#!/bin/sh
/sbin/pfctl -F all
/sbin/pfctl -t uhc_filter -T kill
/sbin/pfctl -f /etc/pf.conf
echo
/sbin/pfctl -sr
echo
echo "# of rules loaded: `/sbin/pfctl -t uhc_filter -Tshow | wc -l`"
echo
