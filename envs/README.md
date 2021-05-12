# Execution environment

## Usage

* Preparation

Get the Singularity image file using datalad

...

* Default mode

```
singularity run ./fmriprep-lts.sif <args>
```

* Fuzzy mode

```
FUZZY=true singularity run ./fmriprep-lts.sif <args>
```

## Build

Pre-requisites
* Docker
* Singularity >= 3.5

`build.sh` builds `fmriprep-lts.sif`:
* Build a Docker image adding fuzzy libmath to a base fmriprep image.
* Convert this image to Singularity
* Push this image to OSF (WIP)



