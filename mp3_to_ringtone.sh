#!/bin/bash

# mp3_to_ringtone.sh
# -John Taylor
# Mar-16-2016

# Convert a portion of a mp3 file to a AAC, suitable for a iPhone ringtone

if [ $# -eq 0 ] ; then
	echo
	echo "$0"
	echo "Usage: [mp3 filename] [start_time] [duration]"
	echo
	echo "start_time and duration are optional"
	echo "defaults: start_time=0  duration=29"
	echo
	exit
fi

if [ $# -eq 2 ] ; then
	start_time=$2
else
	start_time=0
fi

if [ $# -eq 3 ] ; then
	duration=$3
else
	duration=29
fi

input=$1
input_short=`echo ${input%.*}_short.mp3 | sed -e 's/ /_/g' | tr -d "'" | tr -d "&"`
ringtone=${input_short%.*}_ring.m4r

# http://stackoverflow.com/a/20295443/452281
ffmpeg -ss ${start_time} -i "${input}" -t ${duration} "${input_short}"

# http://apple.stackexchange.com/a/26102/13040
afconvert "${input_short}" -o "${ringtone}" -q 127 -b 128000 -f m4af -d aac

echo
echo "${input_short}"
echo
ls -l "${input}" "${input_short}" "${ringtone}"
echo
echo If this file looks satisfactory, then run this command:
echo
echo open "${ringtone}"
echo
echo

