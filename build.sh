#! /usr/bin/env sh

set -ex
# SET THE FOLLOWING VARIABLES
# image name
IMAGE=elasticdns
VERSION=`cat VERSION`

docker build -t $IMAGE:$VERSION .