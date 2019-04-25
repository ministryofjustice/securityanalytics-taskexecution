resource "aws_s3_bucket" "results" {
  bucket = "${terraform.workspace}-${var.app_name}-${var.task_name}-results"
  acl    = "private"

  # only allow terraform to delete a non empty bucket if this is a transient workspace
  # i.e. not dev, qa prod &c
  force_destroy = "${var.transient_workspace}"

  # TODO add lifecyle rules for archiving older results

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  # we don't need versioning since all results files are expected to be written once
  # and not updated, they will also have a timestamp in their name
  versioning {
    enabled = false
  }
  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
