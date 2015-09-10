#!/bin/sh

OUTPUT="/etc/pf.uhc.txt"
BACKUP_DEST="/etc/pf_backups"
NOW=`date +"%Y%m%d_%H%M%S"`

REQUIRE="apnic.txt"
if [ ! -e ${REQUIRE} ] ; then
	echo
	echo "required file not found: ${REQUIRE}"
	echo "aborting"
	exit
else
	echo "found required file: ${REQUIRE}"
fi

REQUIRE="afrinic.txt"
if [ ! -e ${REQUIRE} ] ; then
	echo
	echo "required file not found: ${REQUIRE}"
	echo "aborting"
	exit
else
	echo "found required file: ${REQUIRE}"
fi

REQUIRE="zzz_Custom.txt"
if [ ! -e ${REQUIRE} ] ; then
	echo
	echo "required file not found: ${REQUIRE}"
	echo "aborting"
	exit
else
	echo "found required file: ${REQUIRE}"
fi

echo
echo "Creating ${OUTPUT}"
mv ${OUTPUT} ${OUTPUT}.${NOW}
gzip -9 ${OUTPUT}.${NOW} && chmod 400 ${OUTPUT}.${NOW}.gz
mv ${OUTPUT}.${NOW}.gz ${BACKUP_DEST}



echo "# Created on: ${NOW}" >> ${OUTPUT}
echo "#" >> ${OUTPUT}
echo "" >> ${OUTPUT}

# zzz_Custom.txt must come first!
F="zzz_Custom.txt"
echo -n "$F  "
echo >> ${OUTPUT}
echo "# Country: $F" >> ${OUTPUT}
echo >> ${OUTPUT}
cat $F | egrep -v "^#" >> ${OUTPUT}
echo >> ${OUTPUT}

for F in `ls apnic.txt afrinic.txt countries/*.txt` ; do
	echo -n "$F  "
	echo >> ${OUTPUT}
	echo "# Country: $F" >> ${OUTPUT}
	echo >> ${OUTPUT}
	cat $F | egrep -v "^#" >> ${OUTPUT}
	echo >> ${OUTPUT}
	echo >> ${OUTPUT}
done
echo
echo "${OUTPUT} contains `grep -v ^# ${OUTPUT} | grep -c /` entries."
chmod 400 /etc/pf.conf ${OUTPUT}



echo
echo
echo
echo "To flush the rules, run this command:"
echo "/sbin/pfctl -F all"
echo
echo "To load rules, run this command:"
echo "/sbin/pfctl -f /etc/pf.conf ; /sbin/pfctl -e"
echo
echo "To view all rules, run this command:"
echo "/sbin/pfctl -v -t uhc_filter -T show | less"
echo
echo
