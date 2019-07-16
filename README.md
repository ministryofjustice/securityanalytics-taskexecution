[![CircleCI](https://circleci.com/gh/ministryofjustice/securityanalytics-taskexecution.svg?style=svg)](https://circleci.com/gh/ministryofjustice/securityanalytics-taskexecution)

# Task execution

This module exists to do two things.

- Provisioning shared resources used to execute tasks
- Providing a terraform task module to task implementations e.g. nmap scanning task

## ECS Cluster

Currently using AWS Fargate in a public VPC. When we have more sustained and predictable loads replacing this with EC2 based instances will provide better value.

## Shared Task Module

This is intended to be used with terraform's module support for github sources. A task would include it by adding e.g.:

```hcl-terraform
module "my_task" {
  source = "github.com/ministryofjustice/securityanalytics-taskexecution//infrastructure/ecs_task"
  ...
}
``` 

Each task is expected to provide its own docker images and other resources required to run the task.

### ECS Task 

The ECS Task module is to be used by any scan that is implemented using ECS. You need to implement 3 things:

 1. The ECR container image for the task
 2. A piece of code that maps requests to environment variables in the container
 3. The results parser that converts the output of the scan in S3 into a JSON message
 
 
 ### Lambda Task
 
 Lambda tasks are much like ECS tasks but use python code to implement the task without using a container. You need to implement 2 things:
 
 1. The lambda that does the scan
 2. The results parser
 
 ### Policy doc extensions
 
 Both lambda and ecs tasks can be configured to take policy doc extensions. These documents can be used to give the scans additional permissions using IAM.
 
 ### Initial subscriptions
 
 There are two option flags that you set when creating a scan:
 
  - subscribe_input_to_scan_initiator 
    - The scan will subscribe to and consume signals to perform a new host level scan from the scan initiator 
  - subscribe_es_to_output
    - The scan will subscribe the analytics platform to the output of this scan. N.B. The output of such a scan should be outputting using the ResultsContext in it's results parser. 