#!/bin/sh

if [ $# -ne 2 ]
then
    echo "Syntax: setup.sh <app_name> <tf_workspace>"
    sleep 30
    exit
fi
cd infrastructure
terraform init -backend-config "bucket=$1-terraform-state"
terraform workspace new $2 || terraform workspace select $2
terraform apply -auto-approve -input=true
# pause in case the user is watching output
sleep 5