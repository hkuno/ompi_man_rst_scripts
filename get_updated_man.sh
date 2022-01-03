#!/bin/bash

destdir=$1

mkdir -p $destdir

function copytodest() {
    local infile=$1
    local indir=$( dirname $infile )
    local outdir=$(cd $destdir; mkdir -p $indir ; cd $indir; pwd -P )
    cp $infile ${outdir}/
}

for f in $( find . -name \*\.[0-9]in ) ; do
    r=$( git log $f | head -3 | grep 2021 |\
         grep '[May|Jun|Jul|Aug|Sep|Oct|Nov|Dec]' )
    [[ -z $r ]] || echo $f
    [[ -z $r ]] || copytodest $f 
done
