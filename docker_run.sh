#!/bin/sh

docker build -t zquest-data . && docker run -v $PWD/output:/zquest/output -v $PWD/quests:/zquest/quests -it zquest-data "$@"
