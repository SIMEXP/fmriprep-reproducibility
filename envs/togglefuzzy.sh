#!/usr/bin/env bash

set -e

if [ -v FUZZY ] && [ $FUZZY == "true" ]
then
    LIB_WRAP='/opt/mca-libmath/libmath.so'
    test -f ${LIB_WRAP} || (echo "ERROR: cannot find ${LIB_WRAP}" && false)
    export LD_PRELOAD="${LIB_WRAP}"
    echo "Preloaded ${LIB_WRAP}"
fi

# Run initial entrypoint
/usr/local/miniconda/bin/fmriprep $*
