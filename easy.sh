#! /usr/bin/env sh

set -e 

echo "Building container image..."
./build.sh
echo "Done"
echo ""
echo ""

echo -n "Input Route 53 hosted zone id: "
read zone
echo -n "Input Route 53 record: "
read record
echo -n "Input the name you want to use for this container: "
read name

echo -n "Input method of credentials('iam','file','environment'): "
read cred_method
if [ $cred_method = "iam" ]; then
    docker run -it --name $name elasticdns:`cat VERSION` --record $record --zone $zone
    
elif [ $cred_method = "environment" ]; then
    echo -n "Input AWS Access Key: "
    read access_key
    echo -n "Input AWS Secret Key: "
    read secret_key
    docker run -it -e "AWS_ACCESS_KEY_ID=$access_key" -e "AWS_SECRET_ACCESS_KEY=secret_key" --name $name elasticdns:`cat VERSION` --record $record --zone $zone

elif [ "$cred_method" == "file" ]; then
    echo -n "Input the absolute path to the credential file to bind-mount inside of the container: "
    read file_path
    docker run -it --mount type=bind,source="$(file_path)"/target,target=/app/.aws/credentials --name $name elasticdns:`cat VERSION` --record $record --zone $zone

else
    echo "Fatal: Credential method unknown."
    exit 1
fi