data "aws_ssm_parameter" "vpc_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/vpc/id"
}

data "aws_ssm_parameter" "elastic_injestion_queue_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/injest_queue/arn"
}

data "aws_ssm_parameter" "elastic_injestion_queue_id" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/injest_queue/id"
}
