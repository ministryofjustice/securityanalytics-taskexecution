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

data "aws_iam_policy_document" "output_bucket_access" {
  statement {
    effect  = "Allow"
    actions = ["s3:PutObject"]

    resources = [
      "${var.results_bucket_arn}/${terraform.workspace}/${var.task_name}",
      "${var.results_bucket_arn}/${terraform.workspace}/${var.task_name}/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    # TODO reduce this scope
    resources = ["*"]
  }
}

resource "aws_iam_role" "task_role" {
  name               = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  assume_role_policy = "${data.aws_iam_policy_document.ecs_trust.json}"

  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_iam_policy" "task_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  policy = "${data.aws_iam_policy_document.output_bucket_access.json}"
}

resource "aws_iam_role_policy_attachment" "task_policy" {
  role       = "${aws_iam_role.task_role.name}"
  policy_arn = "${aws_iam_policy.task_policy.arn}"
}
