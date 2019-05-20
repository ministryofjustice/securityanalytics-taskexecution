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
    profile        = "sec-an"
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

variable "transient_workspace" {
  default = false
}

# default to scanme.nmap.org if you haven't defined a list of hosts elsewhere
# (we use scan_hosts.auto.tfvars to ensure it isn't checked in to github)
variable "scan_hosts" {
  type    = "list"
  default = ["scanme.nmap.org"]
}

provider "aws" {
  region = "${var.aws_region}"

  # N.B. To support all authentication use cases, we expect the local environment variables to provide auth details.
  allowed_account_ids = ["${var.account_id}"]
}

#############################################
# Resources
#############################################

module "ecs_cluster" {
  source   = "ecs_cluster"
  app_name = "${var.app_name}"
}
