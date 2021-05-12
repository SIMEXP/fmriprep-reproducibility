#!/usr/bin/env bash

set -e

if [ -v FUZZY ] && [ $FUZZY == "true" ]
then
    LIB_WRAP='/lib/fuzzy/docker/resources/libmath/libmath.so'
    test -f ${LIB_WRAP} || (echo "ERROR: cannot find ${LIB_WRAP}" && false)
    export LD_PRELOAD="${LIB_WRAP} /usr/lib/x86_64-linux-gnu/libdl.so"
    echo "Preloaded ${LIB_WRAP}"
fi

# Run initial entrypoint
/usr/local/miniconda/bin/fmriprep $*
