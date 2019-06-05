data "aws_caller_identity" "account" {
}

data "aws_iam_policy_document" "task_trigger_policy" {
  # So the task trigger can pull task requests off of the task queue
  statement {
    effect = "Allow"

    actions = [
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage",
      "sqs:GetQueueAttributes",
    ]

    resources = [aws_sqs_queue.trigger_queue.arn]
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

  # Only needed when running ecs inside a private vpc
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

resource "aws_iam_policy" "task_trigger_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}-task-trigger"
  policy = data.aws_iam_policy_document.task_trigger_policy.json
}

resource "aws_iam_role_policy_attachment" "task_trigger_policy" {
  role       = aws_iam_role.task_trigger_role.name
  policy_arn = aws_iam_policy.task_trigger_policy.arn
}

