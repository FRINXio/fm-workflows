FROM python:2.7-alpine

# Install dependencies for cryptography
RUN apk add gcc musl-dev python-dev libffi-dev openssl-dev cargo

RUN pip install --no-cache-dir cryptography==2.1.4
RUN pip install --no-cache-dir MockSSH==1.4.5

RUN apk add --no-cache --upgrade bash
RUN apk add --update openssh
RUN apk add --update iptables
RUN apk add openjdk11

# Install dependencies for ncclient
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt

RUN pip install ncclient
RUN pip install pathlib

RUN apk add ulogd

WORKDIR /sample-topology
COPY ./ ./

ADD  https://license.frinx.io/download/netconf-testtool-1.4.2-Oxygen-SR2.4_2_9_rc1-frinxodl-executable.jar /./netconf-testtool/
