data "aws_iam_role" "sns_logging" {
  name = "${var.ssm_source_stage}-${var.app_name}-sns-logging"
}

resource "aws_sns_topic" "scan_initiator" {
  name         = "${terraform.workspace}-${var.app_name}-scan-initiator"
  display_name = "SNS topic to notify scanners to initiate planned scheduled scans"

  sqs_failure_feedback_role_arn    = "${data.aws_iam_role.sns_logging.arn}"
  sqs_success_feedback_role_arn    = "${data.aws_iam_role.sns_logging.arn}"
  sqs_success_feedback_sample_rate = 5

  # TODO enable sns encryption
  # kms_master_key_id = "aws/sns"
}

data "aws_iam_policy_document" "scan_notify_sub_perms" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        "${aws_sns_topic.scan_initiator.arn}",
      ]
    }

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    # Allow any one in our account and region to subscribe
    # TODO could add a tag filter to require the APP_NAME to match too
    resources = [
      "arn:aws:sqs:${var.aws_region}:${var.account_id}:*",
    ]
  }
}

resource "aws_sqs_queue_policy" "scan_initiation_" {
  queue_url = "${aws_sqs_queue.scan_delay_queue.id}"
  policy    = "${data.aws_iam_policy_document.scan_notify_sub_perms.json}"
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  topic_arn            = "${aws_sns_topic.scan_initiator.arn}"
  protocol             = "sqs"
  endpoint             = "${aws_sqs_queue.scan_delay_queue.arn}"
  raw_message_delivery = false
}