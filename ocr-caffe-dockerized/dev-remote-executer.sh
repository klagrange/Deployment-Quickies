#!/bin/bash

IMAGE_NAME="XXX"

[ ! -z $1 ] || { echo "command not provided"; exit 1; }
[ ! -z `docker images -aq ${IMAGE_NAME}` ] || {
  docker build -t ${IMAGE_NAME} .
}

if [ $1 = "PRE-COMMIT" ]; then
  cmd="docker run -v `pwd`:/app -i ${IMAGE_NAME} ${*:2}"
else
  cmd="docker run -v `pwd`:/app -it ${IMAGE_NAME} $@"
fi

eval $cmd
