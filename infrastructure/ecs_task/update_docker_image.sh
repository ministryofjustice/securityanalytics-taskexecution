#!/usr/bin/env bash

eval "$(aws ecr get-login --profile=$5 --no-include-email --region $4)"
docker build -t $1 $3
if [ $? -eq 0 ]
then
    docker tag $1:latest $2:latest
    docker push $2:latest
else
    return 1
fi