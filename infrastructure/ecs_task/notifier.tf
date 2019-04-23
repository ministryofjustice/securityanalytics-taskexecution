resource "aws_sns_topic" "task_results" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-results"
}

data "aws_ssm_parameter" "elastic_injestion_queue" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/injest_queue/arn"
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  count     = "${var.subscribe_elastic_to_notifier}"
  topic_arn = "${aws_sns_topic.task_results.arn}"
  protocol  = "sqs"
  endpoint  = "${data.aws_ssm_parameter.elastic_injestion_queue.value}"
}
