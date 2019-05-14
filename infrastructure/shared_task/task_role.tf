data "aws_iam_policy_document" "output_bucket_access" {
  statement {
    effect  = "Allow"
    actions = ["s3:PutObject"]

    resources = [
      "${aws_s3_bucket.results.arn}",
      "${aws_s3_bucket.results.arn}/*",
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

resource "aws_iam_policy" "task_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  policy = "${data.aws_iam_policy_document.output_bucket_access.json}"
}

resource "aws_iam_role_policy_attachment" "task_policy" {
  role       = "${var.task_role_name}"
  policy_arn = "${aws_iam_policy.task_policy.arn}"
}

data "aws_iam_policy_document" "lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_trigger_role" {
  name               = "${terraform.workspace}-${var.app_name}-${var.task_name}-trigger"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_trust.json}"

  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
