FROM poldracklab/fmriprep:20.2.0

# Verificarlo
RUN apt-get -y update && apt install -y llvm-8 llvm-8-dev clang-8 libmpfr-dev autotools-dev automake

RUN git clone https://github.com/verificarlo/verificarlo.git && \
    (cd verificarlo && git checkout v0.4.2 && ./autogen.sh && \
    ./configure --without-flang --with-llvm=$(llvm-config-8 --prefix))

RUN (cd verificarlo && make && make install)

ENV VFC_BACKENDS 'libinterflop_mca.so --precision-binary32=24 --precision-binary64=53 --mode=mca'

# libmathwrapper
RUN git clone https://github.com/verificarlo/fuzzy.git /lib/fuzzy && \
    (cd /lib/fuzzy/docker/resources/libmath && make)

# Keep track of the Dockerfile
ADD Dockerfile /etc 

# Entrypoint
ADD togglefuzzy.sh /bin
ENTRYPOINT /bin/togglefuzzy
