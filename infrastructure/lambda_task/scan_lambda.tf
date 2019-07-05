resource "aws_lambda_permission" "sqs_invoke" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scan_lambda.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_iam_policy.task_trigger_policy.arn
}

resource "aws_lambda_event_source_mapping" "scan_lambda_trigger" {
  depends_on       = [aws_lambda_permission.sqs_invoke]
  event_source_arn = aws_sqs_queue.trigger_queue.arn
  function_name    = aws_lambda_function.scan_lambda.arn
  enabled          = true
  batch_size       = 1
}

module "scan-lambda_consumer_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "${var.task_name}-task-scan-lambda-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "${var.task_name}/task-scan-lambda"
  source_arn       = aws_lambda_function.scan_lambda.arn
}

resource "aws_lambda_function" "scan_lambda" {
  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-scan-lambda"
  handler          = var.scan_lambda
  role             = aws_iam_role.task_trigger_role.arn
  runtime          = "python3.7"
  filename         = var.lambda_zip
  source_code_hash = var.lambda_hash

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
    data.aws_ssm_parameter.tasks_layer.value
  ]

  tracing_config {
    mode = var.use_xray ? "Active" : "PassThrough"
  }

  environment {
    variables = {
      REGION    = var.aws_region
      STAGE     = terraform.workspace
      APP_NAME  = var.app_name
      TASK_NAME = var.task_name
      USE_XRAY  = var.use_xray
    }
  }

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}
