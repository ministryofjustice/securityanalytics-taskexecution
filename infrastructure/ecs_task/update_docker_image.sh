#!/bin/sh

# Developers will likely have multiple amazon environments setup using profiles, but the build
# uses environment variables. Support both.
if [ "$AWS_ACCESS_KEY_ID" == "" ]; then
    eval "$(aws ecr get-login --profile=$5 --no-include-email --region $4)"
else
    eval "$(aws ecr get-login --no-include-email --region $4)"
fi
docker build -t $1 $3
if [ $? -eq 0 ]
then
    docker tag $1:latest $2:latest
    docker push $2:latest
else
    return 1
fi