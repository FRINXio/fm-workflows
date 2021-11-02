FROM python:3.6.10-buster

WORKDIR /home/app


### Install application setup
RUN pip3 install psycopg2 marshmallow-dataclass jinja2 python_graphql_client==0.4.3
RUN pip3 install frinx-conductor-client frinx-conductor-workers
RUN apt-get update
RUN apt-get -y install nano


ENV X_FROM=fm-workflows


COPY ./workers ./workers
COPY ./workflows ./workflows

COPY ./devices ./devices

WORKDIR /home/app/workers
CMD [ "python3", "main.py" ]
