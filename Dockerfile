FROM python:3.7

RUN mkdir -p /usr/src/creepy-server/server
WORKDIR /usr/src/creepy-server/server

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD python server.py
