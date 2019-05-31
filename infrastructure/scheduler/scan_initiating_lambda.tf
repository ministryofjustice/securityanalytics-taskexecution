resource "aws_lambda_function" "scan_initiator" {

  function_name    = "${terraform.workspace}-${var.app_name}-scan-initiator"
  handler          = "scan_initiator.scan_initiator.initiate_scans"
  role             = "${aws_iam_role.scan_initiator.arn}"
  runtime          = "python3.7"
  filename         = "${local.scheduler_zip}"
  source_code_hash = "${data.external.scheduler_zip.result.hash}"

  layers = [
    "${data.aws_ssm_parameter.utils_layer.value}",
  ]

  environment {
    variables = {
      REGION    = "${var.aws_region}"
      STAGE     = "${terraform.workspace}"
      APP_NAME  = "${var.app_name}"
    }
  }

  tags = {
    workspace = "${terraform.workspace}"
    app_name  = "${var.app_name}"
  }
}

data "aws_iam_policy_document" "scan_initiator_perms" {
  # So the task trigger can find the locations of e.g. queues
  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameters",
    ]

    resources = [
      "*",
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

  statement {
    effect = "Allow"

    actions = [
      "sqs:Send*",
    ]

    # TODO need access to the actual queue when not using the test queue
    resources = ["${aws_sqs_queue.scan_delay_queue.arn}"]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem"
    ]

    resources = ["${aws_dynamodb_table.planned_scans.arn}"]
  }
}

resource "aws_iam_role" "scan_initiator" {
  name               = "${terraform.workspace}-${var.app_name}-scan-initiator"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_trust.json}"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}

resource "aws_iam_policy" "scan_initiator_perms" {
  name   = "${terraform.workspace}-${var.app_name}-scan-initiator"
  policy = "${data.aws_iam_policy_document.scan_initiator_perms.json}"
}

resource "aws_iam_role_policy_attachment" "scan_initiator_perms" {
  role       = "${aws_iam_role.scan_initiator.name}"
  policy_arn = "${aws_iam_policy.scan_initiator_perms.id}"
}