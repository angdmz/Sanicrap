FROM python:3.8-alpine

RUN apk update \
    && apk add build-base

RUN mkdir -p /opt/project
WORKDIR /opt/project
ADD requirements.txt .
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install pytest
RUN pip install ipython