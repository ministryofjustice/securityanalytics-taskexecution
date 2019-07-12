

module "dns_dashboard" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/dashboards/dns_and_dead_letter.dash.json"

  object_substitutions = {
    next_planned_scan  = module.next_planned_scan.object_id
    dead_letters       = data.aws_ssm_parameter.dead_letter_index_pattern.value
    changed_addresses  = module.resolved_address_changes_vis.object_id
    changed_hosts      = module.resolved_host_changes_vis.object_id
    resolved_addresses = module.num_resolved_addresses.object_id
    resolved_hosts     = module.num_resolved_hosts.object_id
    upcoming_scans     = module.upcoming_scans.object_id
    recent_scans       = module.recently_scanned.object_id
    address_filter     = module.address_filter.object_id
    host_filter        = module.host_filter.object_id
  }

  object_type  = "dashboard"
  object_title = "DNS Ingestion and Dead Letters"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}

module "ai_dns_dlq_dashboard" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/dashboards/ai_dns_dlq.dash.json"

  object_substitutions = {
    dead_letters      = data.aws_ssm_parameter.dead_letter_index_pattern.value
    changed_addresses = module.resolved_address_changes_vis.object_id
    changed_hosts     = module.resolved_host_changes_vis.object_id
  }

  object_type  = "dashboard"
  object_title = "Actionable items: DNS changes and DLQs"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}
