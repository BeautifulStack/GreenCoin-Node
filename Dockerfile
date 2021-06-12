FROM python:3.8-alpine3.13

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD gunicorn --workers 2 --bind 0.0.0.0:5000 app:app