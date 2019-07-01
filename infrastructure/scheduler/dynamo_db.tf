locals {
  plan_index = "ToScan"
}

resource "aws_dynamodb_table" "planned_scans" {
  name = "${terraform.workspace}-${var.app_name}-scan-plan"

  # TODO could well be cheaper to provision rather than pay per request
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Address"

  attribute {
    name = "Address"
    type = "S"
  }

  attribute {
    name = "PlannedScanTime"
    type = "N"
  }

  global_secondary_index {
    name               = local.plan_index
    hash_key           = "Address"
    range_key          = "PlannedScanTime"
    projection_type    = "INCLUDE"
    non_key_attributes = ["DnsIngestTime"]
  }

  # This table doesn't feed elastic, it is purely there to determine when to scan
  # no need for streams
  stream_enabled = false

  # TODO add server side encryption

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}

resource "aws_dynamodb_table" "resolved_hosts" {
  name = "${terraform.workspace}-${var.app_name}-resolved-hosts"

  # TODO could well be cheaper to provision rather than pay per request
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Host"
  range_key    = "DnsIngestTime"

  attribute {
    name = "Host"
    type = "S"
  }

  attribute {
    name = "DnsIngestTime"
    type = "N"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # TODO add server side encryption

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}

resource "aws_dynamodb_table" "resolved_addresses" {
  name = "${terraform.workspace}-${var.app_name}-resolved-addresses"

  # TODO could well be cheaper to provision rather than pay per request
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Address"
  range_key    = "DnsIngestTime"

  attribute {
    name = "Address"
    type = "S"
  }

  attribute {
    name = "DnsIngestTime"
    type = "N"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # TODO add server side encryption

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}

resource "aws_dynamodb_table" "address_info" {
  name = "${terraform.workspace}-${var.app_name}-address-info"

  # TODO could well be cheaper to provision rather than pay per request
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Address"

  attribute {
    name = "Address"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # TODO add server side encryption

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}
