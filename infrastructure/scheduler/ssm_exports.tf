resource "aws_ssm_parameter" "plan_db_id" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/id"
  description = "Id of the dynamo db used for the scheduler"
  type        = "String"
  value       = "${aws_dynamodb_table.planned_scans.id}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "plan_db_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/arn"
  description = "Arn of the dynamo db used for the scheduler"
  type        = "String"
  value       = "${aws_dynamodb_table.planned_scans.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "route53_ingest_role" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/route53/role/arn"
  description = "Arn of the role assumed when ingesting route 53 zones"
  type        = "String"
  value       = "${var.route53_role}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "config_period" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/period"
  description = "Configures the period the dns ingestor plans scans over"
  type        = "String"
  value       = "${var.planning_period_seconds}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "config_buckets" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/buckets"
  description = "Configures how many buckets the planner is setup to use"
  type        = "String"
  value       = "${var.planning_buckets}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "config_log_unhandled" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/log_unhandled"
  description = "Arn of the role assumed when ingesting route 53 zones"
  type        = "String"
  value       = "${var.log_unhandled ? "True" : "False"}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}