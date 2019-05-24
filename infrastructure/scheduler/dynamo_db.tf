resource "aws_dynamodb_table" "planned_scans" {
  name           = "${terraform.workspace}-${var.app_name}-scan-schedule"
  # TODO could well be cheaper to provision rather than pay per request
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Address"
  range_key      = "DnsIngestTime"

  attribute {
    name = "Address"
    type = "S"
  }

  attribute {
    name = "DnsIngestTime"
    type = "S"
  }

  attribute {
    name = "PlannedScanTime"
    type = "N"
  }

  local_secondary_index {
    name               = "ToScan"
    range_key          = "PlannedScanTime"
    projection_type    = "INCLUDE"
    non_key_attributes = ["Address", "HostsResolvingToAddress"]
  }

  # TODO add server side encryption

  tags = {
    workspace = "${terraform.workspace}"
    app_name  = "${var.app_name}"
  }
}