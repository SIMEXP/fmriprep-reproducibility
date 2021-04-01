#!/bin/bash

PROJECT_DIR=../../fmriprep-lts
OPENNEURO=$PROJECT_DIR/inputs/openneuro/
SING_IMG=fmriprep-20.2.1lts.sif
FMRIPREP_CONTAINER=$PROJECT_DIR/envs/$SING_IMG
# user variables
TEST=false # whether to print the commands or launch them
SLURM=false # whether to submit slurm jobs or raw cmd
ACCOUNT= # slurm account name
MAIL_USER= # mail for job status

# argument parser
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --test)
    TEST=true
    shift # past argument
    ;;
    --slurm)
    SLURM=true
    shift # past argument
    ;;
    -a|--account)
    ACCOUNT="$2"
    shift # past argument
    shift # past value
    ;;
    -m|--mail)
    MAIL_USER="$2"
    shift # past argument
    shift # past value
    ;;
esac
done

echo "TEST = ${TEST}"
echo "SLURM = ${SLURM}"
echo "ACCOUNT = ${ACCOUNT}"
echo "MAIL_USER = ${MAIL_USER}"

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
        # slurm cmd
        if [ "$SLURM" = true ] ; then
            mkdir -p /scratch/$USER/.slurm
            read -r -d '' CMD <<- EOM
                sbatch
                --account=$ACCOUNT
                --job-name=fmriprep_$DATASET-$PARTICIPANT_%A_%a.job
                --mail-user=$MAIL_USER
                --output=/scratch/%u/.slurm/fmriprep_$DATASET-$PARTICIPANT_%A_%a.out
                --error=/scratch/%u/.slurm/fmriprep_$DATASET-$PARTICIPANT_%A_%a.err
                slurm/fmriprep-slurm.bash $DATASET $PARTICIPANT $SING_IMG
EOM
        # raw cmd
        else
            read -r -d '' CMD <<- EOM
                raw singularity command
EOM
        fi
        # print command
        if [ "$TEST" = true ] ; then
            echo $CMD
        # execute command
        else
            $CMD
        fi
    done
done
