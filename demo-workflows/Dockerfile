FROM python:3.6.10-buster

WORKDIR /home/app

COPY ./workers ./workers
COPY ./workflows ./workflows

COPY ./devices ./devices
COPY ./importDevices.py ./workers/importDevices.py

### Install application setup
RUN pip3 install psycopg2 marshmallow-dataclass jinja2
RUN pip3 install frinx-conductor-client frinx-conductor-workers

ENV X_FROM=fm-workflows

WORKDIR /home/app/workers
CMD [ "python3", "main.py" ]