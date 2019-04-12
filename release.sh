#! /usr/bin/env sh

set -e

# SET THE FOLLOWING VARIABLES
IMAGE=elasticdns
# ensure we're up to date
git pull
# get version
version=`cat VERSION`
echo "version: $version"
# run build
./build.sh
# tag it
git add -A
git commit -m "version $version"
git tag -a "$version" -m "version $version"
git push
git push --tags
