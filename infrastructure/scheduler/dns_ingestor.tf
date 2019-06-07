module "dns_ingestor_dead_letters" {
  // source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region = var.aws_region
  app_name = var.app_name
  account_id = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray = var.use_xray
  recorder_name = "dns-ingestor-DLQ"
  s3_bucket = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix = "task_execution/${aws_lambda_function.ingest_dns.function_name}"
  source_arn = aws_lambda_function.scan_initiator.arn
}

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

  tracing_config {
    mode = var.use_xray ? "Active" : "PassThrough"
  }

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
      USE_XRAY = var.use_xray
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

