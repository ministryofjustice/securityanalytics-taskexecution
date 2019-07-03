resource "aws_ssm_parameter" "public_subnets" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/task_trigger/role/arn"
  description = "The task trigger role for this task"
  type        = "StringList"
  value       = aws_iam_role.task_trigger_role.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "task_queue_consumer_role" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/queue_consumer/role"
  description = "The task queue consumer role"
  type        = "String"
  value       = aws_iam_role.task_trigger_role.name
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "task_queue_consumer_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/queue_consumer/role/arn"
  description = "The task queue consumer role"
  type        = "String"
  value       = aws_iam_role.task_trigger_role.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "results_processor" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/results/role/arn"
  description = "The results processor role"
  type        = "String"
  value       = aws_iam_role.results_parse_role.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "task_queue" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/task_queue/arn"
  description = "The job queue ARN"
  type        = "String"
  value       = aws_sqs_queue.trigger_queue.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "task_queue_url" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/task_queue/url"
  description = "The job queue URL"
  type        = "String"
  value       = aws_sqs_queue.trigger_queue.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "results_notifier" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/results/arn"
  description = "The results broadcaster"
  type        = "String"
  value       = aws_sns_topic.task_results.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

