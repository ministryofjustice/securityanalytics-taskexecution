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

module "delay_queue_notifier_glue" {
  // two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/sqs_sns_glue"

  // It is sometimes useful for the developers of the project to use a local version of the task
  // execution project. This enables them to develop the task execution project and the nmap scanner
  // (or other future tasks), at the same time, without requiring the task execution changes to be
  // pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  // devs will have to comment in/out this line as and when they need
  //  source = "../../../securityanalytics-sharedcode/infrastructure/sqs_sns_glue"

  aws_region       = "${var.aws_region}"
  account_id       = "${var.account_id}"
  app_name         = "${var.app_name}"
  ssm_source_stage = "${var.ssm_source_stage}"
  glue_name        = "delay-notify-glue"
  sns_topic_arn    = "${aws_sns_topic.scan_initiator.arn}"
  sqs_queue_arn    = "${aws_sqs_queue.scan_delay_queue.arn}"
}
