FROM python:3.8.2

RUN apt-get update
RUN apt-get install -y postgresql-client

COPY . /opt/mobilian/app/
WORKDIR /opt/mobilian/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
