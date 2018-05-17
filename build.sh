#! /usr/bin/env sh

# SET THE FOLLOWING VARIABLES
# image name
IMAGE=elasticdns
VERSION=`cat VERSION`

docker build -q -t $IMAGE:$VERSION .