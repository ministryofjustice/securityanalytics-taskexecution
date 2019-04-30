data "aws_ssm_parameter" "task_queue" {
  name = "/${var.app_name}/${terraform.workspace}/tasks/nmap/task_queue/arn"
}
