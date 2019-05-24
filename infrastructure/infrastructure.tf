#############################################
# Backend setup
#############################################

terraform {
  backend "s3" {
    # This is configured using the -backend-config parameter with 'terraform init'
    bucket         = ""
    dynamodb_table = "sec-an-terraform-locks"
    key            = "task-exec/terraform.tfstate"
    region         = "eu-west-2"                   # london
  }
}

#############################################
# Variables used across the whole application
#############################################

variable "aws_region" {
  default = "eu-west-2" # london
}

# Set this variable with your app.auto.tfvars file or enter it manually when prompted
variable "app_name" {}

variable "account_id" {}

variable "ssm_source_stage" {
  default = "DEFAULT"
}

variable "known_deployment_stages" {
  type    = "list"
  default = ["dev", "qa", "prod"]
}

variable "ingest_schedule" {
  type = "string"
  # This is cron(ish) syntax every day at midnight
  default = "0 0 * * ? *"
}

variable "route53_role" {
  type = "string"
  description = "The role that must be assumed to read route 53 info, needed since the source is likey to be in another account"
}

provider "aws" {
  region = "${var.aws_region}"

  # N.B. To support all authentication use cases, we expect the local environment variables to provide auth details.
  allowed_account_ids = ["${var.account_id}"]
}

#############################################
# Resources
#############################################

locals {
  # When a build is done as a user locally, or when building a stage e.g. dev/qa/prod we use
  # the workspace name e.g. progers or dev
  # When the circle ci build is run we override the var.ssm_source_stage to explicitly tell it
  # to use the resources in dev. Change
  ssm_source_stage = "${var.ssm_source_stage == "DEFAULT" ? terraform.workspace : var.ssm_source_stage}"
  transient_workspace = "${!contains(var.known_deployment_stages, terraform.workspace)}"
}

module "ecs_cluster" {
  source   = "ecs_cluster"
  app_name = "${var.app_name}"
}

module "scheduler" {
  source   = "scheduler"
  aws_region = "${var.aws_region}"
  account_id = "${var.account_id}"
  app_name = "${var.app_name}"
  ssm_source_stage = "${local.ssm_source_stage}"
  ingest_schedule = "${var.ingest_schedule}"
  route53_role = "${var.route53_role}"
}
