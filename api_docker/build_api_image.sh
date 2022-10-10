# !/usr/bin/sh

mkdir ./api_docker/src

cp requirements.txt ./api_docker/src/requirements.txt

cp -r api api_docker/src

docker image build api_docker/. -t pauldechorgnat/cdc_demo_api

rm -r ./api_docker/src
