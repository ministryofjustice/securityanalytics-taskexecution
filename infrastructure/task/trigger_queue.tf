data "aws_iam_policy_document" "trigger_queue_policy_iam" {

  statement {
    actions = [
      "sqs:SendMessage",
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        "arn:aws:sns:${var.aws_region}:${var.account_id}:*",
      ]
    }

    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    resources = [aws_sqs_queue.trigger_queue.arn]
  }
}

resource "aws_sqs_queue_policy" "trigger_queue_policy" {
  queue_url = aws_sqs_queue.trigger_queue.id
  policy    = data.aws_iam_policy_document.trigger_queue_policy_iam.json
}

resource "aws_sqs_queue" "trigger_queue" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-task-queue"

  # TODO set settings for kms master key

  redrive_policy = jsonencode({
    deadLetterTargetArn = module.task_queue_dead_letters.arn
    maxReceiveCount     = 1
  })

  tags = {
    task_name = var.task_name
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

module "task_queue_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "${var.task_name}-task-queue-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "${var.task_name}/task-queue"
  source_arn       = aws_sqs_queue.trigger_queue.arn
}
