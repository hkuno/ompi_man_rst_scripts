#!/bin/bash

out1=""
function finish {
    /bin/rm -rf $out1
}
out1=$( mktemp --suffix="$( whoami ).allrefs.txt" )

out=allrefs.txt

cat /dev/null > $out

cnt=0
for f in $( find . -type f -name \*rst | grep -vw index.rst ) ; do
    head -n 1 $f | grep '.. _' >> $out1
    cnt=$(( cnt + 1 ))
done

cat $out1 | tr 'A-Z''a-z' | sort -u > $out
echo $cnt
