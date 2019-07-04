resource "aws_lambda_permission" "sqs_invoke" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.queue_consumer.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = module.taskmodule.task_queue
}

resource "aws_lambda_event_source_mapping" "ingestor_queue_trigger" {
  depends_on       = [aws_lambda_permission.sqs_invoke]
  event_source_arn = module.taskmodule.task_queue
  function_name    = aws_lambda_function.queue_consumer.arn
  enabled          = true
  batch_size       = 1
}

module "task_queue_consumer_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "${var.task_name}-task-queue-consumer-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "${var.task_name}/task-queue-consumer"
  source_arn       = aws_lambda_function.queue_consumer.arn
}

resource "aws_lambda_function" "queue_consumer" {
  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-task-queue-consumer"
  handler          = var.param_parse_lambda
  role             = module.taskmodule.trigger_role_arn
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
