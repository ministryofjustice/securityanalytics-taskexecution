module "sync_address_info" {
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/dynamo_elastic_sync"

  # source = "../../../securityanalytics-analyticsplatform/infrastructure/dynamo_elastic_sync"
  account_id       = var.account_id
  app_name         = var.app_name
  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray

  dynamodb_stream_arn    = aws_dynamodb_table.address_info.stream_arn
  syncer_name            = "address-info"
  non_temporal_key_field = "Address"
}

module "sync_resolved_addresses" {
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/dynamo_elastic_sync"

  # source = "../../../securityanalytics-analyticsplatform/infrastructure/dynamo_elastic_sync"
  account_id       = var.account_id
  app_name         = var.app_name
  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray

  dynamodb_stream_arn    = aws_dynamodb_table.resolved_addresses.stream_arn
  syncer_name            = "resolved-addresses"
  set_column_to_diff     = "Hosts"
  non_temporal_key_field = "Address"
  temporal_key_field     = "DnsIngestTime"
}

module "sync_resolved_hosts" {
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/dynamo_elastic_sync"

  # source = "../../../securityanalytics-analyticsplatform/infrastructure/dynamo_elastic_sync"
  account_id       = var.account_id
  app_name         = var.app_name
  aws_region       = var.aws_region
  account_id = var.account_id
  app_name = var.app_name
  aws_region = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray

  dynamodb_stream_arn    = aws_dynamodb_table.resolved_hosts.stream_arn
  syncer_name            = "resolved-hosts"
  set_column_to_diff     = "Addresses"
  non_temporal_key_field = "Host"
  temporal_key_field     = "DnsIngestTime"
}