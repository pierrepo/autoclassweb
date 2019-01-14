# autoclass@web documentation

## Installation on a production server

### Install Docker
```
$ apt install -y docker.io
```
Verify version:
```
$ docker --version
Docker version 18.06.1-ce, build e68fc7a
```

### Install docker-compose

Check docker-compose last release at <https://github.com/docker/compose/releases>. In this example, it's release 1.23.2.

Then download and install docker-compose:
```
$ curl -L https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
$ chmod +x /usr/local/bin/docker-compose
```

Check version:
```
# docker-compose --version
docker-compose version 1.23.2, build 1110ad01
```

### Install autoclass@web

```
$ cd /opt
$ git clone https://github.com/pierrepo/autoclassweb.git
$ cd autoclassweb
```

### Configure the application

1. Create the application configuration file `.env` from the template:
    ```
    $ cp .env-template .env
    ```
    Update the `.env` file accordingly. Pay attention to the variable `FLASK_SERVER_URL`
2. If needed, update the `docker-compose.yml` file. For instance, in the nginx configuration section, replace `8000` by the desired port.


### Build docker images
```
$ docker-compose build
```

###  Run docker images
```
$ docker-compose up -d
```

Autoclass@web is now accessible at `FLASK_SERVER_URL` (see `.env` file).

Results files are available in `/opt/autoclassweb/results` and logs file in `/opt/autoclassweb/logs`.



## Installation for a quick demo and development

### Install [AutoClass C](https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/):

```
$ wget https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz
$ tar zxvf autoclass-c-3-3-6.tar.gz
$ rm -f autoclass-c-3-3-6.tar.gz
export PATH=$PATH:$(pwd)/autoclass-c
```
If you are using a 64-bit operating system, you also need to install the standard 32-bit C libraries:
```
$ sudo apt-get install -y libc6-i386
```

### Download the project files:
```
$ git clone https://github.com/pierrepo/autoclassweb.git
```

### Configure the application in the `.env` file:
```
$ cd autoclassweb
$ cp .env-template .env
```

### Install and configure Python virtual environment

1. Install pipenv
    ```
    $ pip3 install --user pipenv
    ```

2. Create virtual environment
    ```
    $ pipenv --three
    ```

3. Install required packages
    ```
    $ pipenv install
    ```

### Run the application:
```
$ make run
```

Autoclass@web is now accessible at <http://127.0.0.1:5000/>


### Optional: with gunicorn

Gunicorn can also be used:
```
$ pipenv run gunicorn -b localhost:8000 -w 4 flaskapp:app
```

autoclass-web in then accessible at <http://127.0.0.1:8000/>


