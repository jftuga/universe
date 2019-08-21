#!/bin/bash

if [ $# -ne 1 ] ; then
    CURRENT=`grep "const version" *.go | tr -d '"' | awk -F= '{print $2}'`
    echo
    echo Current version is: ${CURRENT}
    echo
    echo Give this version on cmd-line as the only cmd-line paramter
    echo
    exit
fi

V=$1
DESC=$1

git tag -a v${V} -m "${DESC}"
git push origin v${V}

echo
echo "Now run:"
echo
echo "goreleaser release --rm-dist"
echo
