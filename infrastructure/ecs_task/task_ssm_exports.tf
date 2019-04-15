resource "aws_ssm_parameter" "public_subnets" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/task_trigger/role/arn"
  description = "The task trigger role for this task"
  type        = "StringList"
  value       = "${aws_iam_role.task_trigger_role.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "security_group" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/security_group/id"
  description = "The task's security group"
  type        = "String"
  value       = "${aws_security_group.task_group.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "image_id" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/image/id"
  description = "The task images id"
  type        = "String"
  value       = "${aws_ecs_task_definition.task.family}:${aws_ecs_task_definition.task.revision}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "task_queue_consumer" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/queue_consumer/role/arn"
  description = "The task queue consumer role"
  type        = "String"
  value       = "${aws_iam_role.task_trigger_role.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "results_processor" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/results/role/arn"
  description = "The results processor role"
  type        = "String"
  value       = "${aws_iam_role.results_parse_role.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "task_queue" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/task_queue/arn"
  description = "The job queue"
  type        = "String"
  value       = "${aws_sqs_queue.trigger_queue.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
