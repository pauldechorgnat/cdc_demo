# !/usr/bin/sh

docker container run --name my_mongo --rm -v `pwd`/mongo_docker/data:/data/db -p 27017:27017 mongo:latest

docker container exec -it my_mongo mongosh