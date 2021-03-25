#!/bin/bash

OPENNEURO=../inputs/openneuro/

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
datalad get -r $OPENNEURO/ds000256/sub-PAT23
# senior female
datalad get -r $OPENNEURO/ds000256/sub-PAT10

# Fieldmaps
# Phase-difference map and at least one magnitude image
# Two phase maps and two magnitude images
# Multiple phase encoded directions ("pepolar")
datalad get -r $OPENNEURO/ds001600/sub-1

# non-parametric structural MR images
# T2w
# SBref
datalad get -r $OPENNEURO/ds001771/sub-36
