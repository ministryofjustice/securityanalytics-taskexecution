data "aws_caller_identity" "account" {}

data "aws_iam_policy_document" "task_trigger_policy" {
  statement {
    effect    = "Allow"
    actions   = ["ecs:RunTask"]
    resources = ["${aws_ecs_task_definition.task.arn}"]
  }

  # So the task trigger can pull task requests off of the task queue
  statement {
    effect = "Allow"

    actions = [
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage",
      "sqs:GetQueueAttributes",
    ]

    resources = ["${var.trigger_queue_arn}"]
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

  # To allow the trigger to pass the execution role to ecs to assume when running the task
  statement {
    effect  = "Allow"
    actions = ["iam:PassRole"]

    resources = [
      "${data.aws_iam_role.ecs_exec_role.arn}",
      "${aws_iam_role.task_role.arn}",
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
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}-trigger"
  policy = "${data.aws_iam_policy_document.task_trigger_policy.json}"
}

resource "aws_iam_role_policy_attachment" "task_trigger_policy" {
  role       = "${var.trigger_role_name}"
  policy_arn = "${aws_iam_policy.task_trigger_policy.arn}"
}
