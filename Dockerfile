FROM python:3.8-slim

ADD . /app

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc

RUN pip install -r requirements.txt

CMD gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
