#!/bin/bash

# Given two files, extract just alphanumeric text from each and compare them

TMPDIR=""
function finish {
    /bin/rm -rf $TMPDIR
}

TMPDIR=$( mktemp -d --suffix=".$( whoami ).checkompiman" )
trap finish EXIT

f1=$1
f2=$2

tmpf1=$( basename $f1 ).txt1
tmpf2=$( basename $f2 ).txt2
tmpf1=${TMPDIR}/$tmpf1
tmpf2=${TMPDIR}/$tmpf2

sed -e "s/[^A-Za-z0-9]//g" $f1 | grep -v PACKAGE | grep -v COPYRIGHT |\
  grep -v "20[12][0-9]" | grep -v MPIMPI > $tmpf1
sed -e "s/[^A-Za-z0-9]//g" $f2 | grep -v PACKAGE | grep -v COPYRIGHT |\
  grep -v "20[12][0-9]" | grep -v MPIMPI > $tmpf2

diff $tmpf1 $tmpf2
