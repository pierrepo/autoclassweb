FROM ubuntu:18.04
LABEL maintainer="Pierre Poulain <pierre.poulain@cupnet.net>"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y wget && \
    apt-get install -y libc6-i386 && \
    apt-get install -y python3 python3-pip && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pipenv

# Create app directory
WORKDIR /app

# Install autoclass-c binary
# https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/
RUN wget https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz && \
    tar zxvf autoclass-c-3-3-6.tar.gz && \
    rm -f autoclass-c-3-3-6.tar.gz

ENV PATH "/app/autoclass-c/:${PATH}"

# Install app dependencies
COPY . /app/

RUN pipenv install

VOLUME /app
EXPOSE 5000

#CMD [ "pipenv", "run", "gunicorn", "--config", "gunicorn.conf", "flaskapp:app" ]
CMD ["make", "run-gunicorn"]
