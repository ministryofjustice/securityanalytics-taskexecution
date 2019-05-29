data "aws_iam_role" "sns_logging" {
  name = "${var.ssm_source_stage}-${var.app_name}-sns-logging"
}

resource "aws_sns_topic" "task_results" {
  name         = "${terraform.workspace}-${var.app_name}-${var.task_name}-results"
  display_name = "SNS topic to distribute ${var.task_name} task results"

  sqs_failure_feedback_role_arn    = "${data.aws_iam_role.sns_logging.arn}"
  sqs_success_feedback_role_arn    = "${data.aws_iam_role.sns_logging.arn}"
  sqs_success_feedback_sample_rate = 5

  # TODO enable sns encryption
  # kms_master_key_id = "aws/sns"
}


locals {
  is_not_integration_test = "${terraform.workspace == var.ssm_source_stage ? (var.subscribe_elastic_to_notifier ? 1 : 0) : 0}"
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  count                = "${local.is_not_integration_test}"
  topic_arn            = "${aws_sns_topic.task_results.arn}"
  protocol             = "sqs"
  endpoint             = "${data.aws_ssm_parameter.elastic_ingestion_queue_arn.value}"
  raw_message_delivery = false
}
