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