resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.results_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.taskmodule.results_bucket_arn
}

resource "aws_s3_bucket_notification" "ingestor_queue_trigger" {
  depends_on = [aws_lambda_permission.s3_invoke]
  bucket     = module.taskmodule.results_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.results_parser.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".tar.gz"
  }
}

resource "aws_lambda_function" "results_parser" {
  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-results-parser"
  handler          = var.results_parse_lambda
  role             = module.taskmodule.results_parser
  runtime          = "python3.7"
  filename         = var.lambda_zip
  source_code_hash = filebase64sha256(var.lambda_zip)

  dead_letter_config {
    target_arn = module.taskmodule.results_dead_letter_queue
  }

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
    data.aws_ssm_parameter.tasks_layer.value
  ]

  tracing_config {
    mode = var.use_xray ? "Active" : "PassThrough"
  }

  timeout = 30

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

