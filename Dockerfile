FROM debian:9.4-slim

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update \
&& apt-get install -y wget \
&& apt-get install -y lib32z1 \
&& apt-get install -y python3 python3-pip

RUN pip3 install pipenv

# Create app directory
WORKDIR /app

# Install autoclass-c binary
# https://ti.arc.nasa.gov/tech/rse/synthesis-projects-applications/autoclass/autoclass-c/
RUN wget https://ti.arc.nasa.gov/m/project/autoclass/autoclass-c-3-3-6.tar.gz \
&& tar zxvf autoclass-c-3-3-6.tar.gz
ENV PATH "/app/autoclass-c/:${PATH}"

# Install app dependencies
COPY . /app/

# Create temp directory
RUN mkdir /app/tmp


RUN pipenv install

VOLUME /app/tmp
EXPOSE 8000

ENV FLASK_APP autoclassweb


#CMD [ "pipenv", "run", "flask", "run" ]
CMD [ "pipenv", "run", "gunicorn", "-b 0.0.0.0:8000", "-w 4", "flaskapp:app" ]