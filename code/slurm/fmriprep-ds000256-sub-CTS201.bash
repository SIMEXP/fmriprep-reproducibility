#!/bin/bash

#SBATCH --account=rrg-pbellec
#SBATCH --array=1-5
#SBATCH --job-name=fmriprep_ds000256-sub-CTS201_%A_%a.job
#SBATCH --output=$HOME/fmriprep_ds000256-sub-CTS201_%A_%a.out
#SBATCH --error=$HOME/fmriprep_ds000256-sub-CTS201_%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=4096M
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

export SINGULARITYENV_FS_LICENSE=$HOME/.freesurfer.txt
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

module load singularity/3.6

#copying input dataset into local scratch space
rsync -rltv --info=progress2 $SCRATCH/fmriprep-lts $SLURM_TMPDIR

singularity run --cleanenv -B $SLURM_TMPDIR/fmriprep-lts:/WORK -B $HOME/.cache/templateflow:/templateflow -B /etc/pki:/etc/pki/ /WORK/envs/fmriprep-20.2.1lts.sif -w /WORK/fmriprep_work --participant-label CTS201 --output-spaces MNI152NLin2009cAsym MNI152NLin6Asym --notrack --write-graph --omp-nthreads 8 --nprocs 16 --mem_mb 65536 --resource-monitor /WORK/inputs/openneuro/ds000256 /WORK/inputs/openneuro/ds000256/derivatives/fmriprep participant 
fmriprep_exitcode=$?
if [ $fmriprep_exitcode -ne 0 ] ; then
    cp -R $SLURM_TMPDIR/fmriprep-lts/fmriprep_work $SCRATCH/fmriprep_ds000256-sub-CTS201_$SLURM_ARRAY_TASK_ID.workdir
fi 
if [ $fmriprep_exitcode -eq 0 ] ; then
    cp $SLURM_TMPDIR/fmriprep-lts/fmriprep_work/fmriprep_wf/resource_monitor.json $SCRATCH/fmriprep_ds000256-sub-CTS201_resource_monitor_$SLURM_ARRAY_TASK_ID.json 
    cp -R $SLURM_TMPDIR/fmriprep-lts/inputs/openneuro/ds000256/derivatives/fmriprep $SCRATCH/fmriprep-ds000256_$SLURM_ARRAY_TASK_ID
fi 
exit $fmriprep_exitcode 
