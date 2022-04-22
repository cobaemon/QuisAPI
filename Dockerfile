FROM python:3.10
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt-get install -y vim less git

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN mkdir /root/src
COPY requirements.txt /root/src
WORKDIR /root/src

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

RUN git clone https://github.com/cobaemon/QuisAPI.git
COPY .env /root/src/QuisAPI
WORKDIR /root/src/QuisAPI

RUN python manage.py makemigrations
RUN python manage.py migrate
CMD exec gunicorn djangoapp.wsgi:application --bind 0.0.0.0:8000 --workers 3
