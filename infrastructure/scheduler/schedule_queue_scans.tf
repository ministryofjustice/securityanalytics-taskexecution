resource "aws_cloudwatch_event_target" "schedule_scan_initiator" {
  rule  = "${aws_cloudwatch_event_rule.schedule_scan_initiator.name}"
  arn   = "${aws_lambda_function.ingest_dns.arn}"
  input = "{}"                                                        # no info needed, just do the scan!
}

resource "aws_cloudwatch_event_rule" "schedule_scan_initiator" {
  name                = "${terraform.workspace}-${var.app_name}-scan-initiator"
  description         = "Reads from the scan plan table and queues scans to be done"
  schedule_expression = "cron(${var.scan_schedule})"
}
