locals {
  max_rules     = 15
  planned_count = "${min(local.max_rules,length(var.scan_hosts))}"
}

resource "random_integer" "time_delay" {
  min   = 0
  max   = 59
  seed  = "${var.scan_hosts[count.index]}"
  count = "${local.planned_count}"
}

resource "aws_cloudwatch_event_target" "task_scheduler" {
  count = "${local.planned_count}"
  rule  = "${aws_cloudwatch_event_rule.task_scheduler_sqs_rule.*.name[count.index]}"
  arn   = "${var.queue_arn}"
  input = "{\"CloudWatchEventHosts\":[\"${join("\",\"",slice(var.scan_hosts, floor(count.index*(length(var.scan_hosts)/local.planned_count)), ceil((count.index+1)*(length(var.scan_hosts)/local.planned_count)) ) )}\"]}"
}

resource "aws_cloudwatch_event_rule" "task_scheduler_sqs_rule" {
  count       = "${local.planned_count}"
  name        = "nmap_task_${terraform.workspace}_${count.index}"
  description = "Add hosts to the queue to run nmap"

  # build cron expression manually based on running each hour
  schedule_expression = "cron(${random_integer.time_delay.*.result[count.index]} * * * ? *)"
}

output "planned_count" {
  value = "${local.planned_count}"
}
