resource "aws_iam_role" "results_parse_role" {
  name               = "${terraform.workspace}-${var.app_name}-${var.task_name}-parse"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_trust.json}"

  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

data "aws_iam_policy_document" "results_parse_policy" {
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

  statement {
    effect  = "Allow"
    actions = ["s3:GetObject"]

    resources = [
      "${aws_s3_bucket.results.arn}",
      "${aws_s3_bucket.results.arn}/*",
    ]
  }

  # So the task trigger can find the locations of e.g. queues
  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameters",
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}:${var.account_id}:parameter/${var.app_name}/${terraform.workspace}/*",
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = ["${aws_sns_topic.task_results.id}"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
    ]

    # TODO reduce this scope
    resources = ["*"]
  }
}

resource "aws_iam_policy" "results_parse_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}-parse"
  policy = "${data.aws_iam_policy_document.results_parse_policy.json}"
}

resource "aws_iam_role_policy_attachment" "results_parse_policy" {
  role       = "${aws_iam_role.results_parse_role.name}"
  policy_arn = "${aws_iam_policy.results_parse_policy.arn}"
}
