resource "aws_sns_topic" "task_results" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-results"
}
