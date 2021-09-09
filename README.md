# Project fmriprep-reproducibility

## Dataset structure

- All inputs (i.e. building blocks from other sources) are located in
  `inputs/`.
- Outputs are available at `outputs/`.
- The code is located in `code/`.

# Installation

The fmriprep-reproducibility rely heavily on [Datalad](https://www.datalad.org/), so make sure it is installed in your environment.

`datalad install -r -R 1 git@github.com:SIMEXP/fmriprep-lts.git`

When the installation finished, you can install the other software dependencies needed by our tool:

`make install`

# Data

We carefully selected various datasets from [openneuro](https://openneuro.org/) to create a versatile dataset categorized by age, sex, and conditions.
It also include different fieldmaps technics and non-parametric structural MR images types.
There is another sub-dataset that consist of different singularity containers that we are using.

To install all the data:

`make data`

For a complete overview of all the used datasets, please read [this](https://github.com/SIMEXP/fmriprep-reproducibility/blob/5e7d0d9b0a84eb3e508478192a15d1e5cdfc5a0d/code/get_data.bash#L20-L37).
And for more information on the singularity containers used, check [this section](#execution-environment).

# Usage

We provide an utility script for any slurm-compatible HPC that can help you spawn your fmriprep processes.

```
run.bash

--submit                whether or not to submit the slurm files
--slurm-script          select on which slurm script you want your experiments to be based on (default: fmriprep-slurm.bash)
--fmriprep-version      which fmriprep container version to use (default: 20.2.1)
--sampling              what sampling method to use between ieee or fuzzy (default: ieee)
-a|--account            slurm account
-m|--mail               mail for slurm notifications
```
The recommended way to test the workflow is:

`./code/run.bash --slurm --account def-XXXX --mail XXX@mail.com`

# Execution environment

## Usage

Singularity images are available in sub-dataset `singularity-images` stored on OSF at https://osf.io/rbu92. The sub-dataset can be installed as follows:

```
datalad install envs/singularity-images
```

The Singularity image can be downloaded as follows:
```
datalad get envs/singularity-images/fmriprep-lts*
```

And it can be used as follows:
```
singularity run ./fmriprep-lts.sif <args>
```

## Fuzzy mode

fmriprep can be executed in "fuzzy" mode as follows:
```
singularity run ./fmriprep-lts-fuzzy-VERSION.sif <args>
```

This mode simulates machine error by introducing random perturbations in the results of mathematical functions. It is used to build a reference variability map in the tests.

## Building images

The Singularity image is built from the official fmriprep Docker image. Building the image requires local installations of:
* Docker
* Singularity >= 3.5

The image is built by running `build.sh` from the base directory of this repo.

Once they are built, images can be pushed to OSF as follows:
```
OSF_TOKEN=<your_personal_token> datalad push --to github
```



