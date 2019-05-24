variable "aws_region" {
  type = "string"
}

variable "app_name" {
  type = "string"
}

variable "account_id" {
  type = "string"
}

variable "ssm_source_stage" {
  type = "string"
}

variable "ingest_schedule" {
  type = "string"
}

variable "route53_role" {
  type = "string"
  description = "The role that must be assumed to read route 53 info, needed since the source is likey to be in another account"
}

variable "planning_period_seconds" {
  type = "string"
  description = "The time over which the planner will spread scans"
  default = "86400" # 24 hours
}

variable "planning_buckets" {
  type = "string"
  description = "The number of buckets the period is split into"
  default = "24" # 24 hours
}

variable "log_unhandled" {
  type = "string"
  description = "Whether to log unhandled dns records when ingesting"
  default = false
}