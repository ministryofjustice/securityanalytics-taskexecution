#############################################
# Backend setup
#############################################

terraform {
  backend "s3" {
    bucket         = "sec-an-terraform-state"
    dynamodb_table = "sec-an-terraform-locks"
    key            = "task-exec/terraform.tfstate"
    region         = "eu-west-2"                   # london
    profile        = "sec-an"
  }
}

#############################################
# Variables used across the whole application
#############################################

variable "aws_region" {
  default = "eu-west-2" # london
}

variable "app_name" {
  default = "sec-an"
}

variable "account_id" {}

variable "transient_workspace" {
  default = false
}

provider "aws" {
  region              = "${var.aws_region}"
  profile             = "${var.app_name}"
  allowed_account_ids = ["${var.account_id}"]
}

#############################################
# Resources
#############################################

module "ecs_cluster" {
  source   = "ecs_cluster"
  app_name = "${var.app_name}"
}