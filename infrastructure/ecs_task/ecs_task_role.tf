data "aws_iam_policy_document" "ecs_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_role" {
  name               = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  assume_role_policy = data.aws_iam_policy_document.ecs_trust.json

  tags = {
    task_name = var.task_name
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_iam_role_policy_attachment" "task_policy" {
  role       = aws_iam_role.task_role.name
  policy_arn = module.taskmodule.s3_bucket_policy_arn
}

