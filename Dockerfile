FROM ubuntu:latest
RUN apt-get update --fix-missing \
  && apt-get install -y python3-pip python3.8-dev  \
  build-essential \
  make \
  gcc \
  swig \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y libpulse-dev
RUN apt-get clean

EXPOSE 5000
RUN mkdir -p /odm_modules
COPY ./common_func /odm_modules/common_func
RUN chmod -R a+rwX /odm_modules/common_func/meta

RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt

COPY ./common_func/db2consv_ee.lic  /usr/local/lib/python3.8/dist-packages/clidriver/license/
RUN chmod -R a+rwX '/usr/local/lib/python3.8/dist-packages/clidriver'
COPY ./common_func/db2consv_ee.lic  /usr/local/lib/python3.6/dist-packages/clidriver/license/
RUN chmod -R a+rwX '/usr/local/lib/python3.6/dist-packages/clidriver'

COPY ./BOX /odm_modules/BOX
RUN chmod -R a+rwX /odm_modules/BOX/cache

COPY . /app
RUN chmod -R a+rwX /app/result


