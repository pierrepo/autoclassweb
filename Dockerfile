FROM ubuntu:20.04
LABEL maintainer="Pierre Poulain <pierre.poulain@cupnet.net>"

# Change default shell
SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt update && \
    apt -y upgrade && \
    apt install -y wget && \
    apt install -y libc6-i386 && \
    apt autoremove -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log

# Create app directory
WORKDIR /app

# Install app files
COPY environment-lock.yml ./
COPY flaskapp ./flaskapp
COPY config.py ./
COPY gunicorn.py ./
COPY export_results.py ./


# Install conda
# See https://hub.docker.com/r/conda/miniconda3/dockerfile
ENV PATH /opt/miniconda3/bin:$PATH
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/miniconda3 && \
    rm -f /tmp/miniconda.sh && \
    conda update conda


# Install conda env
ARG conda_env=autoclassweb
RUN conda env create -f environment-lock.yml && \
    conda clean -afy
ENV PATH /opt/miniconda3/envs/${conda_env}/bin:$PATH

# Install autoclass-c binary
# https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/
RUN wget --quiet https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz && \
    tar zxvf autoclass-c-3-3-6.tar.gz && \
    rm -f autoclass-c-3-3-6.tar.gz
ENV PATH "/app/autoclass-c/:${PATH}"

# Create shared directories
RUN mkdir -p /app/{config,logs,results}

# Expose volume and port
VOLUME /app/config
VOLUME /app/logs
VOLUME /app/results
EXPOSE 5000

# CMD ["gunicorn", "--config", "gunicorn.py", "flaskapp:app"]

