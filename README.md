# AutoClassWeb

AutoClassWeb is a web interface to [AutoClass C](https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/), an unsupervised Bayesian classification system developped by the NASA.

It utilizes [AutoClassWrapper](https://github.com/pierrepo/autoclasswrapper), a Python wrapper for AutoClass C. 

## Installation

Documentation is available [here](https://pierrepo.github.io/autoclassweb/).


## Docker 

Build:
```
$ docker build . -t autoclassweb
```

Run:
```
$ docker run -p 5000:5000 -v $(pwd)/config:/app/config -v $(pwd)/logs:/app/logs -v $(pwd)/results:/app/results autoclassweb:latest
```
