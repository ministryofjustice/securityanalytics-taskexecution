data "aws_ssm_parameter" "vpc_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/vpc/id"
}

data "aws_ssm_parameter" "elastic_ingestion_queue_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/ingest_queue/arn"
}

data "aws_ssm_parameter" "elastic_ingestion_queue_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/ingest_queue/id"
}

