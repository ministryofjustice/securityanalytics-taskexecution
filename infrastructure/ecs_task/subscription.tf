data "aws_iam_policy_document" "notify_topic_policy" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        data.aws_ssm_parameter.scan_initiation_topic.value,
      ]
    }

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      module.taskmodule.task_queue,
    ]
  }
}

resource "aws_sqs_queue_policy" "queue_policy" {
  count     = local.is_not_integration_test
  queue_url = module.taskmodule.task_queue_url
  policy    = data.aws_iam_policy_document.notify_topic_policy.json
}

locals {
  is_not_integration_test = terraform.workspace == var.ssm_source_stage ? var.subscribe_input_to_scan_initiator ? 1 : 0 : 0
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  count                = local.is_not_integration_test
  topic_arn            = data.aws_ssm_parameter.scan_initiation_topic.value
  protocol             = "sqs"
  endpoint             = module.taskmodule.task_queue
  raw_message_delivery = true
}

