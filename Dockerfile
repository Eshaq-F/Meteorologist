FROM python:3.8.5-alpine

RUN mkdir /django
WORKDIR /django
EXPOSE 8000

RUN apk add --no-cache mariadb-connector-c-dev
RUN apk update && apk add python3 python3-dev gcc libc-dev mysql-dev build-base
RUN apk add netcat-openbsd

COPY restapi/requirements.txt /django/requirements.txt

RUN pip3 install -r requirements.txt

COPY restapi /django

RUN sleep 15
RUN python manage.py migrate
CMD python manage.py runserver 0.0.0.0:8000