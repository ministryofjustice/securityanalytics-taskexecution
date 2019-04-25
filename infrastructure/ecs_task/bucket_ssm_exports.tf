resource "aws_ssm_parameter" "results_bucket_id" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/s3/results/id"
  description = "The results bucket's name"
  type        = "String"
  value       = "${aws_s3_bucket.results.id}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_ssm_parameter" "results_bucket_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/tasks/${var.task_name}/s3/results/arn"
  description = "The results bucket's arn"
  type        = "String"
  value       = "${aws_s3_bucket.results.arn}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
