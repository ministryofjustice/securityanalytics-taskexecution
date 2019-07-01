data "aws_ssm_parameter" "vpc_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/vpc/id"
}

data "aws_ssm_parameter" "elastic_ingestion_queue_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/ingest_queue/arn"
}

data "aws_ssm_parameter" "elastic_ingestion_queue_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/ingest_queue/id"
}

data "aws_ssm_parameter" "dead_letter_bucket_name" {
  name = "/${var.app_name}/${var.ssm_source_stage}/s3/dead_letters/name"
}

data "aws_ssm_parameter" "dead_letter_bucket_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/s3/dead_letters/arn"
}

data "aws_ssm_parameter" "scan_info_table" {
  name = "/${var.app_name}/${var.ssm_source_stage}/scheduler/dynamodb/address_info/arn"
}