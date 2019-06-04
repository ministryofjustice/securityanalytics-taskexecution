variable "app_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "account_id" {
}

variable "task_name" {
  type = string
}

variable "docker_dir" {
  type = string
}

variable "cpu" {
  type = string
}

variable "memory" {
  type = string
}

variable "sources_hash" {
  type = string
}

variable "docker_hash" {
  type = string
}

variable "subscribe_elastic_to_notifier" {
  type        = string
  description = "If this task produces elastic compatible output, this can be used to connect the task directly to elastic."
}

variable "ssm_source_stage" {
  type        = string
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}

variable "transient_workspace" {
  type        = string
  description = "Used when doing integration tests to make the results buckets created deleteable."
}

