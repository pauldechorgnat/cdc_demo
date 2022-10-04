# !/usr/bin/sh

cp requirements.txt ./docker/requirements.txt

cp -r api docker

docker image build docker/. -t my_image