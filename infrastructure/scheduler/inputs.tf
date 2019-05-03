variable "app_name" {
  type = "string"
}

variable "task_name" {
  type = "string"
}

variable "queue_url" {
  type = "string"
}

variable "queue_arn" {
  type = "string"
}

variable "scan_hosts" {
  type = "list"
}

variable "ssm_source_stage" {
  type        = "string"
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}

variable "transient_workspace" {
  type        = "string"
  description = "Used when doing integration tests to make the results buckets created deleteable."
}
