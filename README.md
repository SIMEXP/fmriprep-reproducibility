# Project fmriprep-reproducibility

## Dataset structure

- All inputs (i.e. building blocks from other sources) are located in
  `inputs/`.
- All custom code is located in `code/`.

# Installation

`datalad install -r -R 1 git@github.com:SIMEXP/fmriprep-lts.git`

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



