#!/bin/bash

PROJECT_DIR=../../fmriprep-lts
OPENNEURO=$PROJECT_DIR/inputs/openneuro/
FMRIPREP_CONTAINER=$PROJECT_DIR/envs/fmriprep-20.2.1lts.sif

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
with open(os.path.join(\"/WORK\", \"code\", \"fmriprep-cmd.json\")) as f: data = json.load(f)
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
with open(os.path.join(\"/WORK\", \"code\", \"fmriprep-cmd.json\")) as f: data = json.load(f)
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

######### Get the container


######### Download the templateflow templates
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
singularity exec -B $PROJECT_DIR:/WORK \
  -B /etc/pki:/etc/pki \
  -B /home/$USER/.cache/templateflow:/templateflow \
  $FMRIPREP_CONTAINER \
  python3 -c """
from templateflow.api import get;
get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])
"""
