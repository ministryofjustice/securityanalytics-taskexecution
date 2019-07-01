data "aws_iam_policy_document" "output_bucket_access" {
  statement {
    effect = "Allow"
    actions = ["s3:PutObject"]

    resources = [
      aws_s3_bucket.results.arn,
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

  # To enable XRAY trace
  statement {
    effect = "Allow"

    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets",
      "xray:GetSamplingStatisticSummaries"
    ]

    # TODO make a better bound here
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "s3_bucket_access_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  policy = data.aws_iam_policy_document.output_bucket_access.json
}

data "aws_iam_policy_document" "lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_trigger_role" {
  name               = "${terraform.workspace}-${var.app_name}-${var.task_name}-trigger"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json

  tags = {
    task_name = var.task_name
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

