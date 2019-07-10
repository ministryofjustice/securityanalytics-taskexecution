variable "app_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
}

variable "task_name" {
  type = string
}

variable "subscribe_input_to_scan_initiator" {
  type = string
}

variable "subscribe_es_to_output" {
  type = string
}

variable "ssm_source_stage" {
  type        = string
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}

variable "transient_workspace" {
  type        = string
  description = "Used when doing integration tests to make the results buckets created deleteable."
}

variable "lambda_zip" {
  type = string
}

variable "lambda_hash" {
  type = string
}

variable "scan_lambda" {
  type = string
}

variable "scan_extension_policy_doc" {
  type        = string
  default     = null
  description = "If you provide a json doc here it will be attached to the parameter parsing lambda's role"
}

variable "results_parse_lambda" {
  type = string
}

variable "results_parse_extension_policy_doc" {
  type        = string
  default     = null
  description = "If you provide a json doc here it will be attached to the results parsing lambda's role"
}

variable "cpu" {
  type = string
}

variable "memory" {
  type = string
}

variable "scan_timeout" {
  type = number
  # Really should never need that long, but 3 seconds is too short now we have doc collections
  default = 2 * 60
}