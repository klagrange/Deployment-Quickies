FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install python-pydot python-pydot-ng graphviz -y
RUN apt-get install curl -y
RUN curl -sSL https://get.haskellstack.org/ | sh

WORKDIR /opt

RUN git clone git://github.com/BurntSushi/erd && \
  cd erd && stack install

COPY ./er/* er/

RUN mkdir pdf

RUN chmod +x ./er/transform.sh

CMD cd ./er && ./transform.sh

