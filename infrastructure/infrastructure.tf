#############################################
# Backend setup
#############################################

terraform {
  backend "s3" {
    # This is configured using the -backend-config parameter with 'terraform init'
    bucket         = ""
    dynamodb_table = "sec-an-terraform-locks"
    key            = "task-exec/terraform.tfstate"
    region         = "eu-west-2" # london
  }
}

#############################################
# Variables used across the whole application
#############################################

variable "aws_region" {
  default = "eu-west-2" # london
}

# Set this variable with your app.auto.tfvars file or enter it manually when prompted
variable "app_name" {
}

variable "account_id" {
}

variable "ssm_source_stage" {
  default = "DEFAULT"
}

variable "known_deployment_stages" {
  type    = list(string)
  default = ["dev", "qa", "prod"]
}

variable "route53_role" {
  type        = string
  description = "The role that must be assumed to read route 53 info, needed since the source is likey to be in another account"
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
  default     = false
}

provider "aws" {
  version = "~> 2.13"
  region  = var.aws_region

  # N.B. To support all authentication use cases, we expect the local environment variables to provide auth details.
  allowed_account_ids = [var.account_id]
}

#############################################
# Resources
#############################################

locals {
  # When a build is done as a user locally, or when building a stage e.g. dev/qa/prod we use
  # the workspace name e.g. progers or dev
  # When the circle ci build is run we override the var.ssm_source_stage to explicitly tell it
  # to use the resources in dev. Change
  ssm_source_stage = var.ssm_source_stage == "DEFAULT" ? terraform.workspace : var.ssm_source_stage

  transient_workspace = false == contains(var.known_deployment_stages, terraform.workspace)
}

module "ecs_cluster" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source   = "./ecs_cluster"
  app_name = var.app_name
}

module "scheduler" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source           = "./scheduler"
  aws_region       = var.aws_region
  account_id       = var.account_id
  app_name         = var.app_name
  ssm_source_stage = local.ssm_source_stage
  route53_role     = var.route53_role
  use_xray         = var.use_xray
}

