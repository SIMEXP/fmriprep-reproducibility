#!/usr/bin/env bash

set -e
set -u

# Run this script from the base repo

FMRIPREP_VERSION=20.2.0

docker build . --build-arg fmriprep_version=${FMRIPREP_VERSION} -f envs/Dockerfile -t fmriprep-lts:${FMRIPREP_VERSION}
docker run -v /var/run/docker.sock:/var/run/docker.sock\
       -v $PWD/envs:/tmp\
       -v $PWD:$PWD\
       -w $PWD\
       quay.io/singularity/docker2singularity -n fmriprep-lts.sif fmriprep-lts:${FMRIPREP_VERSION} 

#singularity build envs/fmriprep-lts.sif docker-daemon://fmriprep-lts:${FMRIPREP_VERSION}
