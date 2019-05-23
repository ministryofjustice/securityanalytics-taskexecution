resource "aws_dynamodb_table" "planned_scans" {
  name           = "${terraform.workspace}-${var.app_name}-scan-schedule"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Id"
  range_key      = "DnsIngestTime"

  attribute {
    name = "Id" # Will be a composite of the address and time
    type = "S"
  }

  attribute {
    name = "DnsIngestTime"
    type = "S"
  }

  attribute {
    name = "PlannedScanTime"
    type = "S"
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