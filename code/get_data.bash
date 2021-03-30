#!/bin/bash

PROJECT_DIR=../../fmriprep-lts
OPENNEURO=$PROJECT_DIR/inputs/openneuro/
FMRIPREP_CONTAINER=$PROJECT_DIR/envs/fmriprep-20.2.1lts.sif

# Here get the container, more specifically for slurm compatibility

## Age
# children male
datalad get -r $OPENNEURO/ds000256/sub-CTS201
# children female
datalad get -r $OPENNEURO/ds000256/sub-CTS210
# young male
datalad get -r $OPENNEURO/ds001748/sub-adult15
# young female
datalad get -r $OPENNEURO/ds001748/sub-adult16
# adult male
datalad get -r $OPENNEURO/ds002338/sub-xp207
# adult female
datalad get -r $OPENNEURO/ds002338/sub-xp201
# senior male
datalad get -r $OPENNEURO/ds002080/sub-PAT23
# senior female
datalad get -r $OPENNEURO/ds002080/sub-PAT10

# Fieldmaps
# Phase-difference map and at least one magnitude image
# Two phase maps and two magnitude images
# Multiple phase encoded directions ("pepolar")
datalad get -r $OPENNEURO/ds001600/sub-1

# non-parametric structural MR images
# T2w
# SBref
datalad get -r $OPENNEURO/ds001771/sub-36

# make sure to download all the templateflow templates
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
singularity exec -B $PROJECT_DIR:/WORK \
  -B /etc/pki:/etc/pki \
  -B /home/$USER/.cache/templateflow:/templateflow \
  $FMRIPREP_CONTAINER \
  python3 -c """
from templateflow.api import get;
get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym', 'OASIS30ANTs', 'MNIPediatricAsym', 'MNIInfant'])
"""
