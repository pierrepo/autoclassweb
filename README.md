# AutoClassWeb

AutoClassWeb is a web interface to [AutoClass C](https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/), an unsupervised Bayesian classification system developped by the NASA.

It utilizes [AutoClassWrapper](https://github.com/pierrepo/autoclasswrapper), a Python wrapper for AutoClass C. 

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
```
$ sudo apt-get install -y libc6-i386
```

Copy config template and update config file `config/autoclassweb.cfg` accordingly:
```bash
$ cp config/autoclassweb-template.cfg config/autoclassweb.cfg
```

Run autoclassweb alone:
```bash
$ make run
```

or with gunicorn:
```bash
$ make run-gunicorn
```

Autoclassweb is then available at <http://127.0.0.1:5000>

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

Autoclassweb is then available at <http://127.0.0.1:5000>

Clean unused images:
```bash
$ make docker-clean
```

A Docker image of [autoclassweb](https://hub.docker.com/r/biocontainers/autoclassweb) is also available in the [Biocontainers](https://biocontainers.pro/) docker repo.


