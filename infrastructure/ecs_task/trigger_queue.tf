resource "aws_sqs_queue" "trigger_queue" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-trigger"

  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
