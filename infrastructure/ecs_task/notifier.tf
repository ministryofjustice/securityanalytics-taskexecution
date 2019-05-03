resource "aws_sns_topic" "task_results" {
  name         = "${terraform.workspace}-${var.app_name}-${var.task_name}-results"
  display_name = "SNS topic to distribute ${var.task_name} task results"
}

data "aws_iam_policy_document" "notify_topic_policy" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        "${aws_sns_topic.task_results.arn}",
      ]
    }

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      "${data.aws_ssm_parameter.elastic_ingestion_queue_arn.value}",
    ]
  }
}

resource "aws_sqs_queue_policy" "queue_policy" {
  queue_url = "${data.aws_ssm_parameter.elastic_ingestion_queue_id.value}"
  policy    = "${data.aws_iam_policy_document.notify_topic_policy.json}"
}

locals {

  is_integration_test = "${terraform.workspace == var.ssm_source_stage ? (var.subscribe_elastic_to_notifier ? 1 : 0) : 0}"
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  count                = "${local.is_integration_test}"
  topic_arn            = "${aws_sns_topic.task_results.arn}"
  protocol             = "sqs"
  endpoint             = "${data.aws_ssm_parameter.elastic_ingestion_queue_arn.value}"
  raw_message_delivery = false
}
