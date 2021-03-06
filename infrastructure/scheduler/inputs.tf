variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "account_id" {
  type = string
}

variable "ssm_source_stage" {
  type = string
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
}

variable "scan_schedule" {
  type = string

  # This is cron(ish) syntax every 15 mins
  default = "0/15 * * * ? *"
}

variable "route53_role" {
  type        = string
  description = "The role that must be assumed to read route 53 info, needed since the source is likey to be in another account"
}

variable "planning_period_seconds" {
  type        = string
  description = "The time over which the planner will spread scans"
  default     = "86400" # 24 hours
}

variable "planning_buckets" {
  type        = string
  description = "The number of buckets the period is split into"
  default     = "96" # 24 hours * 4 subdivisions into 15 min buckets
}

variable "log_unhandled" {
  type        = string
  description = "Whether to log unhandled dns records when ingesting"
  default     = false
}

variable "rate_limit_slowdown" {
  type        = string
  description = "We are allowed 5 requests a second, if this number was e.g. 10, then we would submit 1 request every 2 seconds"
  default     = 10
}
