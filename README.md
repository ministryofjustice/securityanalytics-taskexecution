[![CircleCI](https://circleci.com/gh/ministryofjustice/securityanalytics-taskexecution.svg?style=svg)](https://circleci.com/gh/ministryofjustice/securityanalytics-taskexecution)

# Task execution

This module exists to do two things.

- Provisioning shared resources used to execute tasks
- Providing a terraform task module to task implementations e.g. nmap scanning task

## Provisioning shared resources

Principally two things

1. The ECS cluster used to run tasks
2. The s3 bucket to which tasks output their results

### ECS Cluster

Currently using AWS Fargate in a public VPC. When we have more sustained and predictable loads replacing this with EC2 based instances will provide better value.

### Results Bucket

Each task will submit it's results to a sub folder of the shared bucket.

## Shared Task Module

This is intended to be used with terraform's module support for github sources. A task would include it by adding e.g.:

```hcl-terraform
module "my_task" {
  source = "github.com/ministryofjustice/securityanalytics-taskexecution//infrastructure/ecs_task"
  ...
}
``` 

Each task is expected to provide its own docker images and other resources required to run the task.