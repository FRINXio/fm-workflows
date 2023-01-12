FROM python:3.6.15-buster

WORKDIR /home/app


### Install application setup
COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get -y install nano


ENV X_FROM=fm-workflows


COPY ./workers ./workers
COPY ./workflows ./workflows
COPY ./devices ./devices

WORKDIR /home/app/workers
CMD [ "python3", "main.py" ]
