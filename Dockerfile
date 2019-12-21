FROM ubuntu:18.04
LABEL maintainer="Pierre Poulain <pierre.poulain@cupnet.net>"

# Change default shell
SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt update && \
    apt -y upgrade && \
    apt install -y wget && \
    apt install -y libc6-i386 && \
    apt purge && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install app dependencies
COPY . /app/

ENV PATH /opt/miniconda3/bin:$PATH

# See https://hub.docker.com/r/continuumio/miniconda3/dockerfile
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/miniconda3 && \
    rm -f /tmp/miniconda.sh && \
    conda init 

ARG conda_env=autoclassweb

RUN conda env create -f environment.yml && \
    conda clean -afy

RUN echo "conda activate ${conda_env}" >> ~/.bashrc
ENV PATH /opt/miniconda3/envs/${conda_env}/bin:$PATH

# Create app directory
WORKDIR /app

# Install autoclass-c binary
# https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/
RUN wget --quiet https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz && \
    tar zxvf autoclass-c-3-3-6.tar.gz && \
    rm -f autoclass-c-3-3-6.tar.gz

ENV PATH "/app/autoclass-c/:${PATH}"

# Install app files
COPY . /app/

# Expose volume and port
VOLUME /app
EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn.conf", "flaskapp:app"]

