#!/bin/bash

DATASET=$1
PARTICIPANT=$2

#SBATCH --account=rrg-pbellec
#SBATCH --array=1-5
#SBATCH --job-name=$DATASET-$PARTICIPANT_repro.job
#SBATCH --output=$SCRATCH/fmriprep-lts/outputs/ieee/current/$DATASET-$PARTICIPANT_repro.out
#SBATCH --error=$SCRATCH/fmriprep-lts/outputs/ieee/current/$DATASET-$PARTICIPANT_repro.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=4096M
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

OUT_DIR=$SCRATCH/fmriprep-lts/outputs/ieee/current/$DATASET-$PARTICIPANT-$SLURM_ARRAY_TASK_ID
mkdir $OUT_DIR
export SINGULARITYENV_FS_LICENSE=$HOME/.freesurfer.txt
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

module load singularity/3.6

# getting dataset into local scratch space
cd $SLURM_TMPDIR
datalad clone ///openneuro
datalad get $DATASET/$PARTICIPANT
rsync -rltv --info=progress2 --exclude="sub*" --exclude="derivatives" /scratch/ltetrel/ds000224-download $SLURM_TMPDIR
rsync -rltv --info=progress2 /scratch/ltetrel/ds000224-download/sub-MSC01 $SLURM_TMPDIR/ds000224-download

singularity run --cleanenv -B $SLURM_TMPDIR:/DATA -B /home/ltetrel/.cache/templateflow:/templateflow -B /etc/pki:/etc/pki/ /lustre03/project/6003287/containers/fmriprep-20.2.1lts.sif -w /DATA/fmriprep_work --participant-label MSC01  --bids-database-dir /DATA/ds000224-download/.pybids_cache  --bids-filter-file /DATA/ds000224-download/.slurm/bids_filters.json   --output-spaces MNI152NLin2009cAsym MNI152NLin6Asym --output-layout bids --notrack --skip_bids_validation --write-graph --omp-nthreads 8 --nprocs 16 --mem_mb 65536 --resource-monitor /DATA/ds000224-download /DATA/ds000224-download/derivatives/fmriprep participant
fmriprep_exitcode=$?
if [ $fmriprep_exitcode -ne 0 ] ; then cp -R $SLURM_TMPDIR/fmriprep_work $OUT_DIR/smriprep_sub-MSC01-$SLURM_ARRAY_TASK_ID.workdir ; fi 
if [ $fmriprep_exitcode -eq 0 ] ; then cp $SLURM_TMPDIR/fmriprep_work/fmriprep_wf/resource_monitor.json $OUT_DIR/smriprep_sub-MSC01_resource_monitor_$SLURM_ARRAY_TASK_ID.json ; fi
if [ $fmriprep_exitcode -eq 0 ] ; then cp -R $SLURM_TMPDIR/ds000224-download/derivatives/fmriprep $OUT_DIR/ ; fi 
exit $fmriprep_exitcode 
