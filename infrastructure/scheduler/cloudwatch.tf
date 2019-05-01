resource "random_integer" "time_delay" {
  min   = 0
  max   = 59
  seed  = "${var.scan_hosts[count.index]}"
  count = "${(length(var.scan_hosts)>80)?80:length(var.scan_hosts)}"
}

resource "aws_cloudwatch_event_target" "task_scheduler" {
  count = "${(length(var.scan_hosts)>80)?80:length(var.scan_hosts)}"
  rule  = "${aws_cloudwatch_event_rule.task_scheduler_sqs_rule.*.name[count.index]}"
  arn   = "${var.queue_arn}"
  input = "{\"CloudWatchEventHosts\":[\"${join("\",\"",slice(var.scan_hosts, floor(count.index*(length(var.scan_hosts)/80)), ceil((count.index+1)*(length(var.scan_hosts)/80)) ) )}\"]}"
}

resource "aws_cloudwatch_event_rule" "task_scheduler_sqs_rule" {
  count       = "${(length(var.scan_hosts)>80)?80:length(var.scan_hosts)}"
  name        = "nmap_task_${count.index}"
  description = "Add hosts to the queue to run nmap"

  # build cron expression manually based on running each hour
  schedule_expression = "cron(${random_integer.time_delay.*.result[count.index]} * * * ? *)"
}
