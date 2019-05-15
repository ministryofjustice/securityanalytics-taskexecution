#!/bin/sh

if [ $# -ne 2 ]
then
    echo "Syntax: build.sh <app_name> <tf_workspace>"
    sleep 30
    exit
fi
cd infrastructure
terraform init -backend-config "bucket=$1-terraform-state"
terraform workspace new $2 || terraform workspace select $2
terraform apply -auto-approve -input=true

sleep 5