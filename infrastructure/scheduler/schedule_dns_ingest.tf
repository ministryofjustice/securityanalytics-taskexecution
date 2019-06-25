resource "aws_cloudwatch_event_target" "schedule_dns_ingest" {
  rule  = aws_cloudwatch_event_rule.schedule_dns_ingest.name
  arn   = aws_lambda_function.ingest_dns.arn
  input = "{}" # no info needed, just do the scan!
}

data "external" "current_time" {
  program = [
    "python",
    "-c",
    # external datasource expects json, simple script to include now's minutes as the value in json
    "import datetime; now = datetime.datetime.now(); print(f\"{{\\\"min\\\":\\\"{now.minute}\\\",\\\"hour\\\":\\\"{now.hour}\\\"}}\")"
  ]
}

locals {
  # Originally this was always midnight, but we had multiple environments all trying to ingest
  # at once which stops any from succeeding, this hack reduces the chances of that happening.
  # It won't invoke when we start up, because the time determined by terraform will already have
  # passed, but see the null resource null_resource.initial_dns_ingest, which will invoke
  # the lambda at startup
  # TODO https://dsdmoj.atlassian.net/browse/SA-123 Share the ingest logic to avoid the duplication
  ingest_schedule = "${tonumber(data.external.current_time.result.min)} ${tonumber(data.external.current_time.result.hour)} * * ? *"
}

resource "aws_cloudwatch_event_rule" "schedule_dns_ingest" {
  name                = "${terraform.workspace}-${var.app_name}-ingest-dns"
  description         = "Ingest dns data to plan scanning"
  schedule_expression = "cron(${local.ingest_schedule})"
}

resource "aws_lambda_permission" "dns_ingest_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest_dns.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule_dns_ingest.arn
}

