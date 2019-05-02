data "aws_iam_policy_document" "trigger_queue_policy_iam" {
  statement {
    actions = ["SQS:SendMessage"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = ["${aws_sqs_queue.trigger_queue.arn}"]
  }
}

resource "aws_sqs_queue_policy" "trigger_queue_policy" {
  queue_url = "${aws_sqs_queue.trigger_queue.id}"
  policy    = "${data.aws_iam_policy_document.trigger_queue_policy_iam.json}"
}

resource "aws_sqs_queue" "trigger_queue" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-trigger"

  tags {
    task_name = "${var.task_name}"
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
