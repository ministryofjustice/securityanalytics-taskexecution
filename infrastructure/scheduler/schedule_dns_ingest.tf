resource "aws_cloudwatch_event_target" "schedule_dns_ingest" {
  rule  = "${aws_cloudwatch_event_rule.task_scheduler_sqs_rule.*.name[count.index]}"
  arn   = "${aws_lambda_function.ingest_dns.arn}"
  input = "{}" # no info needed, just do the scan!
}

resource "aws_cloudwatch_event_rule" "task_scheduler_sqs_rule" {
  name        = "${terraform.workspace}-${var.app_name}-ingest-dns"
  description = "Ingest dns data to plan scanning"
  schedule_expression = "cron(${var.ingest_schedule})"
}
