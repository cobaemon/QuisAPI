FROM python:3.10
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt-get install -y vim less git postgresql-client

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

ARG DJANGO_SECRET_KEY=DJANGO_SECRET_KEY
ARG POSTGRES_DB=POSTGRES_DB
ARG POSTGRES_USER=POSTGRES_USER
ARG POSTGRES_PASSWORD=POSTGRES_PASSWORD
ARG POSTGRES_HOST=POSTGRES_HOST
ARG POSTGRES_PORT=POSTGRES_PORT

ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
ENV POSTGRES_DB=$POSTGRES_DB
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_PORT=$POSTGRES_PORT

RUN mkdir -p /var/www/quisapi
COPY . /var/www/quisapi

WORKDIR /var/www/quisapi

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r ./requirements/product.txt

RUN python manage.py collectstatic
RUN python manage.py makemigrations quisapi
