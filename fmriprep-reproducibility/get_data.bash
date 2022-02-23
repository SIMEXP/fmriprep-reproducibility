#!/bin/bash

CURR_DIR=$(pwd)
SCRIPT_DIR=$(readlink -e $(dirname $0))
PROJECT_DIR=..
OPENNEURO=$PROJECT_DIR/inputs/openneuro/
TEMPLATEFLOW_DIR=/home/$USER/.cache/templateflow
SING_IMG=fmriprep-lts-20.2.0.sif
FMRIPREP_CONTAINER=$PROJECT_DIR/envs/singularity-images/$SING_IMG

cd $SCRIPT_DIR

######### Get the containers
cd $PROJECT_DIR/envs/singularity-images/
git annex enableremote osf-annex2-storage
cd $SCRIPT_DIR
datalad get $PROJECT_DIR/envs/singularity-images/fmriprep-lts*

######### Get the raw data
## Age
# children male ds000256/sub-CTS201
# children female ds000256/sub-CTS210
# young male ds001748/sub-adult15
# young female ds001748/sub-adult16
# adult male /ds002338/sub-xp207
# adult female /ds002338/sub-xp201
# senior male ds002080/sub-PAT23
# senior female ds002080/sub-PAT10
## Fieldmaps
# Phase-difference map and at least one magnitude image
# Two phase maps and two magnitude images
# Multiple phase encoded directions ("pepolar")
# ds001600/sub-1
## Non-parametric structural MR images
# T2w
# SBref
# ds001771/sub-36

# read all dataset keys
DATASET_KEYS=($(singularity exec -B $PROJECT_DIR:/WORK $FMRIPREP_CONTAINER \
  python3 -c """
import os
import json
with open(os.path.join(\"/WORK\", \"fmriprep-reproducibility\", \"fmriprep-cmd.json\")) as f: data = json.load(f)
list_keys = \" \".join(data.keys())
print(list_keys)
  """
  ))

# Loop through all datasets
for DATASET in ${DATASET_KEYS[@]}
do
    # read all participant keys
    export SINGULARITYENV_DATASET=$DATASET
	PARTICIPANT_KEYS=($(singularity exec -B $PROJECT_DIR:/WORK $FMRIPREP_CONTAINER \
      python3 -c """
import os
import json
with open(os.path.join(\"/WORK\", \"fmriprep-reproducibility\", \"fmriprep-cmd.json\")) as f: data = json.load(f)
list_keys = \" \".join(data[os.environ.get(\"DATASET\")].keys())
print(list_keys)
      """
      ))
    # loop through all participants
    for PARTICIPANT in ${PARTICIPANT_KEYS[@]}
    do
        datalad get -r $OPENNEURO/$DATASET/$PARTICIPANT
    done
done

######### Download the templateflow templates
mkdir -p $TEMPLATEFLOW_DIR
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
singularity exec -B $PROJECT_DIR:/WORK \
  -B /etc/pki:/etc/pki \
  -B $TEMPLATEFLOW_DIR:/templateflow \
  $FMRIPREP_CONTAINER \
  python3 -c """
from templateflow.api import get;
get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])
"""

cd $CURR_DIR
