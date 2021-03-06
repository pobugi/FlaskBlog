FROM ubuntu:20.04

MAINTAINER name EvgenyS "pobugi@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y sqlite3 libsqlite3-dev

COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

ENTRYPOINT [ "python3" ]

CMD [ "./app.py" ]