FROM python:3.6.10-buster

WORKDIR /home/app

COPY ./workers ./workers
COPY ./workflows ./workflows
COPY ./conductor-client ./conductor-client

COPY ./devices ./devices
COPY ./importDevices.py ./workers/importDevices.py

### Install application setup
WORKDIR /home/app/conductor-client/python
RUN pip3 install setuptools
RUN python3 setup.py install
RUN pip3 install psycopg2
RUN pip3 install marshmallow-dataclass
RUN pip3 install jinja2

WORKDIR /home/app/workers
CMD [ "python3", "main.py" ]

WORKDIR /home/app/