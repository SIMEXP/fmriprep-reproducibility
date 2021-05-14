#!/usr/bin/env bash

set -e
set -u

DOCKERFILE_DIR=$(readlink -e $(dirname $0))
ENVSPATH=$(realpath ${DOCKERFILE_DIR}/../../envs)

function docker2singularity(){
    local docker_image=$1
    local sing_image_name=$2

    local mounts="-v ${ENVSPATH}:/tmp -v $PWD:$PWD -w $PWD"
    
    docker run -v /var/run/docker.sock:/var/run/docker.sock ${mounts}\
           quay.io/singularity/docker2singularity -n ${sing_image_name}.sif ${docker_image}

    docker run  ${mounts}\
       --entrypoint='/bin/bash'\
       quay.io/singularity/docker2singularity -c "rm -Rf /tmp/${sing_image_name}.{tar,build,build.tar} && chown ${UID}:${UID} /tmp/${sing_image_name}.sif"
    
}

FMRIPREP_VERSION=20.2.0

# Build regular (non-fuzzy) image from Poldrack lab Docker image
#docker2singularity poldracklab/fmriprep:${FMRIPREP_VERSION} fmriprep-lts-${FMRIPREP_VERSION}

# Build fuzzy image
docker build . --build-arg fmriprep_version=${FMRIPREP_VERSION} -f ${DOCKERFILE_DIR}/Dockerfile -t fmriprep-lts-fuzzy:${FMRIPREP_VERSION}

docker2singularity fmriprep-lts-fuzzy:${FMRIPREP_VERSION} fmriprep-lts-fuzzy-${FMRIPREP_VERSION}

