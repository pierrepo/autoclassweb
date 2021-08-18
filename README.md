# AutoClassWeb

[![License: BSD](https://img.shields.io/badge/License-BSD-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5215902.svg)](https://doi.org/10.5281/zenodo.5215902)
[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/pierrepo/autoclassweb/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/pierrepo/autoclassweb)

AutoClassWeb is a web interface to [AutoClass C](https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/), an unsupervised Bayesian classification system developed by the NASA.

It utilizes [AutoClassWrapper](https://github.com/pierrepo/autoclasswrapper), a Python wrapper for AutoClass C. 

## Installation for use on a local machine

See step-by-step instructions: <https://github.com/pierrepo/autoclassweb-app>


## Installation for use on a web server

See step-by-step instructions: <https://github.com/pierrepo/autoclassweb-server>


## Installation for development

Clone the project:
```bash
$ git clone https://github.com/pierrepo/autoclassweb.git
$ cd autoclassweb
```

Create and activate a conda environment:
```bash
$ conda env create -f environment.yml
$ conda activate autoclassweb
```

Install [AutoClass C](https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/):

```bash
$ wget https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz
$ tar zxvf autoclass-c-3-3-6.tar.gz
$ rm -f autoclass-c-3-3-6.tar.gz
$ export PATH=$PATH:$(pwd)/autoclass-c
```
If you use a 64-bit operating system, install the standard 32-bit C libraries:
```bash
$ sudo apt install -y libc6-i386
```

Copy config template and update config file `config/autoclassweb.cfg` accordingly:
```bash
$ cp config/autoclassweb-template.cfg config/autoclassweb.cfg
```

Run AutoClassWeb alone:
```bash
$ make run
```

or with gunicorn:
```bash
$ make run-gunicorn
```

AutoClassWeb is then available at <http://127.0.0.1:5000>

## Docker 

Install Docker with the following [instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

Build image:
```bash
$ make docker-build
```

Run container:
```bash
$ make docker-run
```

AutoClassWeb is then available at <http://127.0.0.1:5000>

Clean unused images:
```bash
$ make docker-clean
```

A Docker image of [AutoClassWeb](https://hub.docker.com/r/biocontainers/autoclassweb) is also available in the [Biocontainers](https://biocontainers.pro/) docker repository.


