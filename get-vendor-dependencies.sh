#!/bin/bash

# use http_proxy if specified
proxy_flag=""
if [ ! -z "$http_proxy" ]; then
  proxy_flag=" --proxy $http_proxy" 
fi

# vendor app dependencies
# https://docs.cloudfoundry.org/buildpacks/python/index.html
sudo pip3 download -r requirements.txt --no-binary=:all: -d vendor $proxy_flag
