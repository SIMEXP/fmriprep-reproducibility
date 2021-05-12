ARG fmriprep_version

# Multistage build

# Not the base image, will be used to copy stuff from
FROM verificarlo/fuzzy:v0.4.1-lapack as fuzzy

# Base image
FROM poldracklab/fmriprep:${fmriprep_version}

# Copy fuzzy environment from fuzzy image
RUN mkdir -p /opt/mca-libmath
COPY --from=fuzzy /opt/mca-libmath/libmath.so /opt/mca-libmath/
COPY --from=fuzzy /usr/local/lib/libinterflop* /usr/local/lib/
ENV VFC_BACKENDS 'libinterflop_mca.so --precision-binary32=24 --precision-binary64=53 --mode=mca'

# An entrypoint to toggle the fuzzy environment
COPY envs/togglefuzzy.sh /bin/
ENTRYPOINT togglefuzzy.sh