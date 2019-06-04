resource "aws_ssm_parameter" "security_group" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/security_group/id"
  description = "The task's security group"
  type        = "String"
  value       = aws_security_group.task_group.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "image_id" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/image/id"
  description = "The task images id"
  type        = "String"
  value       = "${aws_ecs_task_definition.task.family}:${aws_ecs_task_definition.task.revision}"
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

