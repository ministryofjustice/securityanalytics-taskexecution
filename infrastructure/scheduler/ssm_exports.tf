resource "aws_ssm_parameter" "plan_db_id" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/scans_planned/id"
  description = "Id of the dynamo db used for the scheduler plan"
  type        = "String"
  value       = aws_dynamodb_table.planned_scans.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "plan_db_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/scans_planned/arn"
  description = "Arn of the dynamo db used for the scheduler plan"
  type        = "String"
  value       = aws_dynamodb_table.planned_scans.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "plan_index" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/scans_planned/plan_index"
  description = "Name of the index we query by"
  type        = "String"
  value       = local.plan_index
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "host_db_id" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/resolved_hosts/id"
  description = "Id of the dynamo db used to record hosts we resolved"
  type        = "String"
  value       = aws_dynamodb_table.resolved_hosts.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "host_db_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/resolved_hosts/arn"
  description = "Arn of the dynamo db used to record hosts we resolved"
  type        = "String"
  value       = aws_dynamodb_table.resolved_hosts.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "address_db_id" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/resolved_addresses/id"
  description = "Id of the dynamo db used to record addresses we resolved"
  type        = "String"
  value       = aws_dynamodb_table.resolved_addresses.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "address_db_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/resolved_addresses/arn"
  description = "Arn of the dynamo db used to record addresses we resolved"
  type        = "String"
  value       = aws_dynamodb_table.resolved_addresses.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "address_info_db_id" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/address_info/id"
  description = "Id of the dynamo db used to store status info about scans"
  type        = "String"
  value       = aws_dynamodb_table.address_info.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "address_info_db_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/dynamodb/address_info/arn"
  description = "Arn of the dynamo db used to store status info about scans"
  type        = "String"
  value       = aws_dynamodb_table.address_info.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "route53_ingest_role" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/route53/role/arn"
  description = "Arn of the role assumed when ingesting route 53 zones"
  type        = "String"
  value       = var.route53_role
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "config_period" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/period"
  description = "Configures the period the dns ingestor plans scans over"
  type        = "String"
  value       = var.planning_period_seconds
  overwrite   = "true"

  tags = {

    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "config_buckets" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/buckets"
  description = "Configures how many buckets the planner is setup to use"
  type        = "String"
  value       = var.planning_buckets
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "config_log_unhandled" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/log_unhandled"
  description = "Arn of the role assumed when ingesting route 53 zones"
  type        = "String"
  value       = var.log_unhandled ? "True" : "False"
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "config_rate_limit_slowdown" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/config/rate_limit_slowdown"
  description = "We are allowed 5 requests a second, if this number was e.g. 10, then we would submit 1 request every 2 seconds"
  type        = "String"
  value       = var.rate_limit_slowdown
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "scan_delay_queue" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/scan_delay_queue"
  description = "The URL of the queue used to delay scan initiation"
  type        = "String"
  value       = aws_sqs_queue.scan_delay_queue.id
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "aws_ssm_parameter" "scan_initiator_topic_arn" {
  name        = "/${var.app_name}/${terraform.workspace}/scheduler/scan_initiator_topic/arn"
  description = "The topic ARN used for the scheduler to notify primary scanners to perform their scans"
  type        = "String"
  value       = aws_sns_topic.scan_initiator.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

