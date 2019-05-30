data "aws_iam_policy_document" "scan_delay_queue_policy" {
  statement {
    actions = ["SQS:SendMessage"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = ["${aws_sqs_queue.scan_delay_queue.arn}"]
  }
}

resource "aws_sqs_queue_policy" "scan_delay_queue_policy" {
  queue_url = "${aws_sqs_queue.scan_delay_queue.id}"
  policy    = "${data.aws_iam_policy_document.scan_delay_queue_policy.json}"
}

resource "aws_sqs_queue" "scan_delay_queue" {
  name = "${terraform.workspace}-${var.app_name}-scan-delay-queue"

  # TODO set settings for e.g. dead letter queue, message retention, and kms master key

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
