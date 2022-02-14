#!/bin/bash

#TMPDIR=""
#function finish {
#    /bin/rm -rf $TMPDIR
#}
#TMPDIR=$( mktemp -d --suffix=".$( whoami ).mpitest" )
#
#trap finish EXIT

APPNAME=$(basename $0)
APPDIR=$(cd $(dirname $0) ; pwd)

MANHOME=/c/git/man_ompi
BUILDDIR=./_build/
BUILDMAN=./_build/man/

# Note: could use mktemp but for easier to debug if known name
TMPDIR=/tmp/ompiman
mkdir -p $TMPDIR
TMPRST=$TMPDIR/tmprst/
mkdir -p $TMPRST
MDTMPRST=$TMPDIR/tmpmdrst/
mkdir -p $MDTMPRST
MDTMPRST=$( cd $MDTMPRST; pwd -P )

BUILDRST=./rst/
mkdir -p $BUILDDIR
mkdir -p $BUILDRST
[[ -d ../rst ]] || mkdir -p ../rst
[[ -L $BUILDDIR/rst ]] || [[ -f $BUILDDIR/rst ]] || ln -sf ../rst $BUILDDIR/

BUILDHTML=./_build/html/
MANDIRS="ompi/mpi/man ompi/mpiext ompi/tools oshmem/shmem/man opal/tools/wrappers oshmem/tools/oshmem_info "

TSTMAN_ORIG=$TMPDIR/tmpman_orig/
TSTMAN_NEW=$TMPDIR/tmpman_new/
TSTMAN_DIFF=$TMPDIR/tmpman_diff/
TSTMAN_TEXT_DIFF=$TMPDIR/tmpman_text_diff/

mkdir -p $BUILDMAN
BUILDRST=$(cd $BUILDRST ; pwd -P )
[[ -f $BUILDRST/conf.py ]] || cp $APPDIR/conf.py $BUILDRST/
[[ -f $BUILDRST/index.rst ]] || cp $APPDIR/index.rst $BUILDRST/

# For each man page, if the man page includes another,
# convert nroff ".so" command to rst ".. include::"
# else use pandoc to convert the man page to rst.
if [[ 1 -eq 1 ]] ; then
    echo "About to convert man to rst"
    SAVEME=$( pwd )
    ERRORFILE=pandoc_man2rst.output
    cat /dev/null > $ERRORFILE
    for d in $MANDIRS ; do
        for f in $( find $d -name \*.\*in ) ; do
            f2=$( echo $f | sed -e "s/\.\([0-9]*\)in/.\1/" )
            out=$TMPRST/${f2}.rst
            # add labels for files that originally included this file
            if [[ $( grep -w '^\.so' $f | wc -l ) -eq 1 ]] ; then
                out=$BUILDRST/${f2}.rst
                echo "converting $f to $out" >> $ERRORFILE
                mkdir -p $( dirname $out )
                fname=$( grep -w '^\.so' $f | awk '{printf"%s.rst",$2}' )
                [[ -z "${fname}" ]] && echo "WARNING: ERROR: See $fname"
                pname=$( basename $out | awk -F\. '{print $1}' )
                pnamelower=$( echo $pname | tr 'A-Z' 'a-z')
                delim=$( echo $pname | sed -e "s/[a-z,A-Z,0-9,_,\-]/=/g" )
                echo ".. _${pnamelower}:" > $out
                echo " " >> $out
                echo $pname >> $out
                echo $delim >> $out
                echo "    .. include_body" >> $out
                echo "" >> $out
                echo ".. include:: ../${fname}" >> $out
                echo "    :start-after: .. include_body" >> $out
                echo "" >> $out
            else
                mkdir -p $( dirname $out )
                echo "converting $f to $out" >> $ERRORFILE
                cd $( dirname $f )
                f2=$( basename $f)
                pandoc -f man -t rst $f2 1> $out 2>> $ERRORFILE
                cd $SAVEME
            fi
        done
    done

    # Check for warning messages
    echo "WARNING messages from $ERRORFILE:" $( grep WARNING $ERRORFILE | wc -l )
fi

# For each man md page
# use pandoc to convert the man page to rst.
if [[ 1 -eq 1 ]] ; then
    echo "About to convert md to rst"
    SAVEME=$( pwd )
    ERRORFILE=pandoc_md2rst.output
    cat /dev/null > $ERRORFILE
    for d in $MANDIRS ; do
        for f in $( find $d -name \*.md ) ; do
            f2=$( echo $f | sed -e "s/\.\([0-9]*\).md/.\1/" )
            out=$MDTMPRST/${f2}.rst
            mkdir -p $( dirname $out )
            echo "converting $f to $out"
            echo "converting $f to $out" >> $ERRORFILE
            cd $( dirname $f )
            f2=$( basename $f)
            pandoc -f gfm -t rst $f2 1> $out 2>> $ERRORFILE
            cd $SAVEME
        done
    done

    # Check for warning messages
    echo "WARNING messages from $ERRORFILE:" $( grep WARNING $ERRORFILE | wc -l )
fi

# fix up rst files
SAVEME=$( pwd )
if [[ 1 -eq 1 ]] ; then
    echo "About to fix up rst"
    date
    for d in $MANDIRS ; do
        for f in $( cd $TMPRST/$d; find . -name \*.rst ) ; do
            infile="$TMPRST/$d/$f"
            out="$BUILDRST/$d/$f"
            mkdir -p $( dirname $out )
            echo "Fixing $infile as $out"
            python3 $APPDIR/fixup_rst.py $infile $out
        done
    done
    date
fi

# fix up rst files generated from md
SAVEME=$( pwd )
if [[ 1 -eq 1 ]] ; then
    echo "About to fix up rst generated from md files"
    date
    for d in $MANDIRS ; do
        if [[ -d $MDTMPRST/$d ]]; then
            for f in $( cd $MDTMPRST/$d; find . -name \*.rst ) ; do
                infile="$MDTMPRST/$d/$f"
                out="$BUILDRST/$d/$f"
                mkdir -p $( dirname $out )
                echo "MD: Fixing $infile as $out"
                python3 $APPDIR/fix_md_rst.py $infile $out
            done
        fi
    done
    date
fi

# ARGH. Tables are hard.
if [[ 1 -eq 1 ]] ; then
    cp $APPDIR/Open-MPI.5.rst $BUILDRST/ompi/mpi/man/man5/Open-MPI.5.rst
fi

# use sphinx-build to create html files
if [[ 0 -eq 1 ]] ; then
    echo "About to create html files"
    date
    SAVEME=$( pwd )
    cd $BUILDDIR
    ERRORFILE=sphinx-build_rst2html.output
    cat /dev/null > $ERRORFILE
    sphinx-build -b html -c rst rst/ html/ >& $ERRORFILE
    cd $SAVEME
    date
fi


# use sphinx-build to create man files
if [[ 0 -eq 1 ]] ; then
    echo "About to create man files"
    date
    ERRORFILE=sphinx-build_rst2man.output
    SAVEME=$( pwd )
    cd $BUILDDIR/
    sphinx-build -vvv -b man -c rst  rst/ man/ >& $ERRORFILE
    cd $SAVEME
date
fi

# check the man pages by comparing against original man pages
j=0
if [[ 0 -eq 1 ]] ; then
    SAVEME=$( pwd -P )
    mkdir -p $TSTMAN_NEW
    TSTMAN_NEW=$( cd $TSTMAN_NEW; pwd -P )
    echo "TSTMAN_NEW is $TSTMAN_NEW"
    echo "TSTMAN_NEW is $TSTMAN_NEW"
    cd $BUILDMAN
    for i in $( /bin/ls ) ; do
        if [[ ! -d $i ]] ; then
            out=${TSTMAN_NEW}/${i}
            ( man ./${i} >& $out ) &
            j=$(( j + 1 ))
            [[ $(( $j%5 )) -eq 0 ]] && wait
        fi
    done
    echo "new man page output in $TSTMAN_NEW"
    cd $SAVEME
fi
wait

if [[ 0 -eq 1 ]] ; then
    mkdir -p $TSTMAN_ORIG
    TSTMAN_ORIG=$( cd $TSTMAN_ORIG; pwd -P )
    SAVEME=$( pwd -P )
    cd $MANHOME
    i=0
    for d in $MANDIRS ; do
        for f in $( find $d -name \*.\*in -type f ) ; do
            if [[ ! -d $TSTMAN_NEW/$i ]] ; then
                sbname=$( basename $f | sed -e "s/in$//" )
                out=$TSTMAN_ORIG/$sbname
                (man ${f} >& $out) &
                i=$(( i + 1 ))
                [[ $(( $i%5 )) -eq 0 ]] && wait
            fi
        done
    done
    cd $SAVEME
    echo "original man page output in $TSTMAN_ORIG"
fi
wait

if [[ 0 -eq 1 ]] ; then
    SAVEME=$( pwd -P )
    TSTMAN_ORIG=$( cd $TSTMAN_ORIG; pwd -P )
    TSTMAN_NEW=$( cd $TSTMAN_NEW; pwd -P )
    outdir_orig="${TSTMAN_ORIG}.seealso"
    mkdir -p $outdir_orig
    outdir_new="${TSTMAN_NEW}.seealso"
    mkdir -p $outdir_new
    echo "Output dirs: $outdir_orig, $outdir_new"

    j=0
    for i in $( /bin/ls $TSTMAN_NEW ) ; do
        if [[ ! -d $TSTMAN_NEW/$i ]] ; then
            f1=${TSTMAN_NEW}/${i}
            f1out=$outdir_new/$i
            ( python3 $APPDIR/extract_seealso.py $f1 >& $f1out )&
            
            f2=${TSTMAN_ORIG}/${i}
            f2out=$outdir_orig/$i
            [[ -f $f2 ]] && (python3 $APPDIR/extract_seealso.py $f2 >& $f2out ) &

        fi
    done
            
    cd "$TSTMAN_NEW.seealso"
    /bin/rm *.diff
    for f in $( ls -l | grep -vw "0 May" | grep -vw total | awk '{print $NF}' ) ; do
        orig="${TSTMAN_ORIG}.seealso"/$f
        if [[ -f $orig ]] ; then
           ( diff $f $orig >& "$f.diff" )&
           j=$(( j + 1 ))
        else
           cp $f $f.diff
        fi
        [[ $(( $j%2 )) -eq 0 ]] && wait
    done
fi
wait

if [[ 0 -eq 1 ]] ; then
    mkdir -p $TSTMAN_ORIG $TSTMAN_NEW $TSTMAN_DIFF $TSTMAN_TEXT_DIFF
    SAVEME=$( pwd -P )
    TSTMAN_ORIG=$( cd $TSTMAN_ORIG; pwd -P )
    TSTMAN_NEW=$( cd $TSTMAN_NEW; pwd -P )
    mkdir -p $TSTMAN_DIFF
    TSTMAN_DIFF=$( cd $TSTMAN_DIFF; pwd -P )
    echo "TSTMAN_DIFF is $TSTMAN_DIFF"
    j=0
    for i in $( /bin/ls $TSTMAN_NEW ) ; do
        if [[ ! -d $TSTMAN_NEW/$i ]] ; then
            out=${TSTMAN_DIFF}/$i
            f1=${TSTMAN_NEW}/${i}
            f2=${TSTMAN_ORIG}/${i}
            if [[ -f $f1 ]] && [[ -f $f2 ]] ; then
                ( diff $f1 $f2 >& $out ) &
                j=$(( j + 1 ))
                [[ $(( $j%5 )) -eq 0 ]] && wait
            else
                echo "Missing: $f1 or $f2"
            fi
        fi
    done
fi
wait


if [[ 0 -eq 1 ]] ; then
    mkdir -p $TSTMAN_ORIG $TSTMAN_NEW $TSTMAN_DIFF $TSTMAN_TEXT_DIFF
    SAVEME=$( pwd -P )
    TSTMAN_ORIG=$( cd $TSTMAN_ORIG; pwd -P )
    TSTMAN_NEW=$( cd $TSTMAN_NEW; pwd -P )
    mkdir -p $TSTMAN_TEXT_DIFF
    TSTMAN_TEXT_DIFF=$( cd $TSTMAN_TEXT_DIFF; pwd -P )
    echo "TSTMAN_TEXT_DIFF is $TSTMAN_TEXT_DIFF"
    j=0
    for i in $( /bin/ls $TSTMAN_NEW ) ; do
        if [[ ! -d $TSTMAN_NEW/$i ]] ; then
            out=${TSTMAN_TEXT_DIFF}/$i
            f1=${TSTMAN_NEW}/${i}
            f2=${TSTMAN_ORIG}/${i}
            if [[ -f $f1 ]] && [[ -f $f2 ]] ; then
                ( ./checktext.sh $f1 $f2 >& $out ) &
                j=$(( j + 1 ))
                [[ $(( $j%5 )) -eq 0 ]] && wait
            fi
        fi
    done
fi
wait

# TO DO LIST:
# Decide what the directory structure should be with docs and man
# Fix the index.rst and make files, which I copied from docs.
