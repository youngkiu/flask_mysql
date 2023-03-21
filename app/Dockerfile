FROM python:3.8.16

RUN apt-get update
RUN apt-get install -y netcat

COPY . /opt/project/app/
WORKDIR /opt/project/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
