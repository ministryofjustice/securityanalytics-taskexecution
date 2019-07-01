module "scan_initiator_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "scan-initiator-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "task_execution/scan-initiator"
  source_arn       = aws_lambda_function.scan_initiator.arn
}

resource "aws_lambda_function" "scan_initiator" {
  depends_on       = [aws_iam_role_policy_attachment.scan_initiator_perms]
  function_name    = "${terraform.workspace}-${var.app_name}-scan-initiator"
  handler          = "scan_initiator.scan_initiator.initiate_scans"
  role             = aws_iam_role.scan_initiator.arn
  runtime          = "python3.7"
  filename         = local.scheduler_zip
  source_code_hash = data.external.scheduler_zip.result.hash

  # If this fell a long way back we might need to schedule a lot of scans so set the timeout
  # to max
  # TODO reduce this when we have more data about worst case times
  timeout = 15 * 60

  dead_letter_config {
    target_arn = module.scan_initiator_dead_letters.arn
  }

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
  ]

  tracing_config {
    mode = var.use_xray ? "Active" : "PassThrough"
  }

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
      "sqs:Send*",
    ]

    resources = [
      aws_sqs_queue.scan_delay_queue.arn,
      module.scan_initiator_dead_letters.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem",
    ]

    resources = [aws_dynamodb_table.planned_scans.arn]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:UpdateItem",
    ]

    resources = [
      aws_dynamodb_table.address_info.arn
    ]
  }
}

resource "aws_iam_role" "scan_initiator" {
  name               = "${terraform.workspace}-${var.app_name}-scan-initiator"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_iam_policy" "scan_initiator_perms" {
  name   = "${terraform.workspace}-${var.app_name}-scan-initiator"
  policy = data.aws_iam_policy_document.scan_initiator_perms.json
}

resource "aws_iam_role_policy_attachment" "scan_initiator_perms" {
  role       = aws_iam_role.scan_initiator.name
  policy_arn = aws_iam_policy.scan_initiator_perms.id
}

