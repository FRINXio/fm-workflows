FROM python:2.7-alpine

# Install dependencies for cryptography
RUN apk add gcc musl-dev python-dev libffi-dev openssl-dev cargo

RUN apk add --no-cache --upgrade bash
RUN apk add --update openssh
RUN apk add --update iptables
RUN apk add openjdk11

# Install dependencies for ncclient
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt

RUN apk add ulogd

WORKDIR /sample-topology
COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

ADD  https://license.frinx.io/download/netconf-testtool-1.4.2-Oxygen-SR2.4_2_10_rc5-frinxodl-SNAPSHOT-executable.jar /./netconf-testtool/
