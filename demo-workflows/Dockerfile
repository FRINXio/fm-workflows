FROM python:3.6.10-buster

WORKDIR /home/app

COPY ./workers ./workers
COPY ./workflows ./workflows

COPY ./devices ./devices
COPY ./importDevices.py ./workers/importDevices.py

### Install application setup
RUN pip3 install psycopg2
RUN pip3 install marshmallow-dataclass
RUN pip3 install jinja2

RUN pip3 install -i https://test.pypi.org/simple/ frinx-conductor-client frinx-conductor-workers

WORKDIR /home/app/workers
CMD [ "python3", "main.py" ]