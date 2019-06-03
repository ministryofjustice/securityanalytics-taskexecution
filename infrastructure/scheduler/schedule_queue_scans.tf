resource "aws_cloudwatch_event_target" "schedule_scan_initiator" {
  rule  = "${aws_cloudwatch_event_rule.schedule_scan_initiator.name}"
  arn   = "${aws_lambda_function.scan_initiator.arn}"
  input = "{}"                                                        # no info needed, just do the scan!
}

resource "aws_cloudwatch_event_rule" "schedule_scan_initiator" {
  name                = "${terraform.workspace}-${var.app_name}-scan-initiator"
  description         = "Reads from the scan plan table and queues scans to be done"
  schedule_expression = "cron(${var.scan_schedule})"
}

resource "aws_lambda_permission" "scan_initiator_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.scan_initiator.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.schedule_scan_initiator.arn}"
}
