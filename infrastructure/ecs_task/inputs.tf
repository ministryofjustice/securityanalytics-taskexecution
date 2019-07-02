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

variable "ssm_source_stage" {
  type        = string
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}

variable "transient_workspace" {
  type        = string
  description = "Used when doing integration tests to make the results buckets created deleteable."
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
}

variable "cpu" {
  type = string
}

variable "memory" {
  type = string
}

# ECS specific
variable "docker_file" {
  type = string
}

variable "docker_combined_hash" {
  type        = "string"
  description = "Since a docker file makes use of external resources e.g. scripts or executables, we need a combined hash of all those resources and the docker file itself to ensure we rebuild docker when any of those resources change"
}

variable "param_parse_lambda" {
  type = string
}

variable "param_parse_extension_policy_doc" {
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

# General
variable "lambda_zip" {
  type = string
}

variable "subscribe_input_to_scan_initiator" {
  type = string
}

variable "subscribe_es_to_output" {
  type = string
}
