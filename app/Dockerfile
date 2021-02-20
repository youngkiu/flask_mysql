FROM python:3.8.2

RUN apt-get update
RUN apt-get install -y postgresql-client

COPY . /opt/project/app/
WORKDIR /opt/project/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
