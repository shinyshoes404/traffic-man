# to build redis docker image for development and testing
# $ export DOCKER_BUILDKIT=1
# $ docker build --no-cache --target redis_stage -t traffic-man-redis-testing .

# to build the production docker image
# $ export DOCKER_BUILDKIT=1
# $ docker build --no-cache -t traffic-man .


FROM python:3.10.1-slim-bullseye AS base


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
    apt full-upgrade -y && \
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


FROM base AS redis_stage
# install redis
# update the bind directive in the redis config to allow outside hosts to access (for testing dev environment only)
RUN apt-get install redis -y && \
    sed -i -e 's/bind 127.0.0.1 ::1/bind 0.0.0.0/' /etc/redis/redis.conf


FROM redis_stage AS python_stage

# set redis config back to bind to 127.0.0.1 for production use
RUN sed -i -e 's/bind 0.0.0.0/bind 127.0.0.1/' /etc/redis/redis.conf

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
    apt-get install python3-pip -y && \
    pip install gunicorn

# copy the entire project into container image, so we can install it
COPY ./ ${PY_APP_DIR}/

# move into the root of the project directory
# install the project using the setup.py file and pip
# remove the entire project
RUN cd ${PY_APP_DIR} && \
    pip install . && \
    rm -R ./*

# copy the file we need to run the api back into the image
COPY ./src/wsgi.py ${PY_APP_DIR}/

#### --- WHAT TO DO WHEN THE CONTAINER STARTS --- ####

#  make sure the default user owns the etc files
#  start the api with gunicorn and the traffic man application
ENTRYPOINT chown -R ${USERNAME}:${USERNAME} ${ETC_DIR} && \
    redis-server --requirepass ${REDIS_PW} --daemonize yes && \
    su ${USERNAME} -c 'start-traffic-man & cd ${PY_APP_DIR} && gunicorn --bind 0.0.0.0:8003 wsgi:sms_api'
