#!/bin/sh

PRJ="my_project"
SRC="${HOME}/Documents/xcode/${PRJ}"
DST="${HOME}/Dropbox/Web-Work/backups"

NOW=`date +"%Y%m%d_%H%M%S"`

TARBALL="${PRJ}--${NOW}.tar.xz"
ARCHIVE="${DST}/${TARBALL}"

cd "${HOME}/Documents/xcode" && tar cJvf "${ARCHIVE}" "${PRJ}" && chmod 400 "${ARCHIVE}"
echo
echo
ls -l "${ARCHIVE}"
echo
echo
