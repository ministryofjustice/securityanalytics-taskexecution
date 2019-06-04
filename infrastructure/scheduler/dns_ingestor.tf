resource "aws_lambda_function" "ingest_dns" {
  function_name    = "${terraform.workspace}-${var.app_name}-ingest-dns"
  handler          = "dns_ingestor.ingest_dns.ingest_dns"
  role             = aws_iam_role.dns_ingestor.arn
  runtime          = "python3.7"
  filename         = local.scheduler_zip
  source_code_hash = data.external.scheduler_zip.result.hash

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
  ]

  # We have to rate limit dns requests, so there are sleeps in the code
  # and this lambda takes quite a lot of time ~9mins with 128MB lambda
  # (setting to the maximum for safety)
  timeout = 15 * 60

  # This lambda runs once a day, so allocate full memory (and therefore cpu)
  # to make it as fast as possible
  # TODO do experiments to determine best cost/speed benefit
  memory_size = "3008"

  environment {
    variables = {
      REGION   = var.aws_region
      STAGE    = terraform.workspace
      APP_NAME = var.app_name
    }
  }

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
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

data "aws_iam_policy_document" "dns_ingestor_perms" {
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
      "dynamodb:*",
    ]

    resources = [aws_dynamodb_table.planned_scans.arn]
  }

  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    resources = [var.route53_role]
  }
}

resource "aws_iam_role" "dns_ingestor" {
  name               = "${terraform.workspace}-${var.app_name}-dns-ingestor"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_iam_role_policy_attachment" "dns_ingestor_perms" {
  role       = aws_iam_role.dns_ingestor.name
  policy_arn = aws_iam_policy.dns_ingestor_perms.id
}

resource "aws_iam_policy" "dns_ingestor_perms" {
  name   = "${terraform.workspace}-${var.app_name}-dns-ingestor"
  policy = data.aws_iam_policy_document.dns_ingestor_perms.json
}

