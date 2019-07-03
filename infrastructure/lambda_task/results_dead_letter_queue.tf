module "results_parser_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "${var.task_name}-results-parser-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "${var.task_name}/results-parser"
  source_arn       = aws_lambda_function.results_parser.arn
}