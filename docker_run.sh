#!/bin/sh

docker build -t zquest-data . && docker run -v $PWD/output:/zquest/output -it zquest-data "$*"
