# syntax = docker/dockerfile:1.0-experimental
### NOTE: The comment line above is critical. It allows for the user of Docker Buildkit to inject secrets in the image at build time ###
# to build docker image
# $ export DOCKER_BUILDKIT=1
# $ docker build -t traffic-man:latest .

FROM python:3.10.1-slim-bullseye


#### ---- ARGS AND ENVS FOR BUILD ---- ####

### - ENVS - ###

# default user
ENV USERNAME=trafficman
# set the python applications root directory
ENV PY_ROOT_DIR=/home/${USERNAME}/python_apps
# set the directory to store your python application
ENV PY_APP_DIR=${PY_ROOT_DIR}/traffic_man
# set app etc dir for log and db file
ENV ETC_DIR=/etc/traffic-man
# set the timezone info
ENV TZ=America/Chicago
# user that will send file
ENV FILE_USER=onedrivefile


#### ---- BASIC SYSTEM SETUP ---- ####

# check for updates 
# then upgrade the base packages
# set timezone
# Set the locale
# install tzdata package (to make timezone work)
# install nano
# disable root user
# create our default user (this user will run the app)
RUN apt-get update && \
    apt-get upgrade -y && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get install locales -y && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    apt-get install tzdata -y && \
    apt-get install nano -y && \
    passwd -l root &&\
    $(useradd -s /bin/bash -m ${USERNAME})

# setting local ENV variables
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


#### ---- PYTHON and APP ---- ####

# create directory for python app
# create etc directory
# make default user the owner of etc directory
# change etc directory permissions to be 700
# install pip3
# use pip to install gunicorn (for api)
RUN mkdir -p ${PY_APP_DIR} && \
    mkdir -p ${ETC_DIR} && \
    chown ${USERNAME}:${USERNAME} ${ETC_DIR} && \
    chmod 700 ${ETC_DIR} && \
    apt-get install python3-pip -y

# copy the entire project into container image, so we can install it
COPY ./ ${PY_APP_DIR}/

# move into the root of the project directory
# install the project using the setup.py file and pip
# remove the entire project
RUN cd ${PY_APP_DIR} && \
    pip install . && \
    rm -R ./*

# copy in our entrypoint file (everything else should be installed)
COPY src/main.py ${PY_APP_DIR}/



#### --- WHAT TO DO WHEN THE CONTAINER STARTS --- ####

#  change ownership recursively of python application directory so that USERNAME has privileges on files copied into image
#  make sure the default user owns the etc files
#  move into the application directory
#  start the application
ENTRYPOINT chown -R ${USERNAME}:${USERNAME} ${PY_ROOT_DIR} && \
    chown -R ${USERNAME}:${USERNAME} ${ETC_DIR} && \
    su ${USERNAME} -c "cd ${PY_APP_DIR} && \
    python3 main.py"
