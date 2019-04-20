#! /usr/bin/env sh

set -e

# SET THE FOLLOWING VARIABLES
IMAGE=elasticdns

# ensure we're up to date
git pull

# get version
releaseDate=`cat VERSION | cut -d- -f1`
currDate=v`date "+%Y.%m.%d"`
patchLevel=`cat VERSION | cut -d- -f2`

if [ $releaseDate == $currDate ];
then
    patchLevel=$((patchLevel+1))
else
    patchLevel=1
fi

version=$currDate"-"$patchLevel
echo "version: $version"
echo $version > VERSION
# run build
./build.sh
# tag it
git add -A
git commit -m "version $version"
git tag -a "$version" -m "version $version"
git push
git push --tags
git push --tags awscc
