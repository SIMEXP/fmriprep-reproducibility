# Execution environment

## Usage

Singularity images are available in sub-dataset `container-images` stored on OSF at https://osf.io/wvz3e. The sub-dataset can be installed as follows:

```
datalad install envs/container-images
```

The Singularity image can be downloaded as follows:
```
datalad get envs/container-images/fmriprep-lts.sif
```

And it can be used as follows:
```
singularity run ./fmriprep-lts.sif <args>
```

## Fuzzy mode

fmriprep can be executed in "fuzzy" mode from the same image:
```
FUZZY=true singularity run ./fmriprep-lts.sif <args>
```

This mode simulates machine error by introducing random perturbations in the results of mathematical functions. It is used to build a reference variability map in the tests.

## Building images

The Singularity image is built from the official fmriprep Docker image. Building the image requires local installations of:
* Docker
* Singularity >= 3.5

The image is built by running `build.sh` from the base directory of this repo.

Once they are built, images can be pushed to OSF as follows:
```
OSF_TOKEN=<your_personal_token> git-annex export HEAD --to osf-export-storage
```



