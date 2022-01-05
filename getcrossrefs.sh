#!/bin/bash

out1=""
function finish {
    /bin/rm -rf $out1
}
out1=$( mktemp --suffix="$( whoami ).allrefs.txt" )

out=allrefs.txt
includeout=includes.txt

cat /dev/null > $out

cnt=0
for f in $( find . -type f -name \*rst | grep -vw index.rst ) ; do
    label=$( head -n 3 $f | grep '.. _' | sed -e "s/.. _//" | awk -F: '{print $1}')
    echo "$label" >> $out1
    cnt=$(( cnt + 1 ))
done

cat $out1 | tr 'A-Z' 'a-z' | sort -u > $out
echo $cnt
