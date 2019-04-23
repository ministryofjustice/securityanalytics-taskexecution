variable "app_name" {
  type = "string"
}

variable "aws_region" {
  type = "string"
}

variable "account_id" {}

variable "task_name" {
  type = "string"
}

variable "docker_dir" {
  type = "string"
}

variable "results_bucket_arn" {
  type = "string"
}

variable "cpu" {
  type = "string"
}

variable "memory" {
  type = "string"
}

variable "sources_hash" {
  type = "string"
}

variable "docker_hash" {
  type = "string"
}

variable "vpc_id" {
  type = "string"
}

variable "subscribe_elastic_to_notifier" {
  type = "string"
}

variable "ssm_source_stage" {
  type = "string"
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}