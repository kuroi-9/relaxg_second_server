FROM python:3.14-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
