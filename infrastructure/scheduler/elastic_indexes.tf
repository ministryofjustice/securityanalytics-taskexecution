module "address_info_index" {
   # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
 source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/elastic_index"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/elastic_index"
  app_name = var.app_name
  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  index_file       = "${path.module}/indexes/address_info.index.json"
  index_name       = "data"
  task_name        = "address_info"
 snapshot_and_history = false
  es_domain = data.aws_ssm_parameter.es_domain.value
}

module "address_info_index_pattern" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name
  aws_region           = var.aws_region
  ssm_source_stage     = var.ssm_source_stage
  task_name            = "address_info"
  object_template      = "${path.module}/indexes/address_info.pattern.json"
  object_substitutions = {}

  object_type  = "index-pattern"
  object_title = "address_info:data:read*"
  es_domain = data.aws_ssm_parameter.es_domain.value
}

module "resolved_addresses_index" {
   # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/elastic_index"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/elastic_index"
  app_name = var.app_name
  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  index_file       = "${path.module}/indexes/resolved_addresses.index.json"
  index_name       = "data"
  task_name        = "resolved_addresses"
 snapshot_and_history = false
  es_domain = data.aws_ssm_parameter.es_domain.value
}

module "resolved_addresses_index_pattern" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name
  aws_region           = var.aws_region
  ssm_source_stage     = var.ssm_source_stage
  task_name            = "resolved_addresses"
  object_template      = "${path.module}/indexes/resolved_addresses.pattern.json"
  object_substitutions = {}

  object_type  = "index-pattern"
  object_title = "resolved_addresses:data:read*"
  es_domain = data.aws_ssm_parameter.es_domain.value
}

module "resolved_hosts_index" {
   # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/elastic_index"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/elastic_index"
  app_name = var.app_name
  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  index_file       = "${path.module}/indexes/resolved_hosts.index.json"
  index_name       = "data"
  task_name        = "resolved_hosts"
 snapshot_and_history = false
  es_domain = data.aws_ssm_parameter.es_domain.value
}

module "resolved_hosts_index_pattern" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

 # It is sometimes useful for the developers of the project to use a local version of the task
 # execution project. This enables them to develop the task execution project and the nmap scanner
 # (or other future tasks), at the same time, without requiring the task execution changes to be
 # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
 # devs will have to comment in/out this line as and when they need
 # source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name
  aws_region           = var.aws_region
  ssm_source_stage     = var.ssm_source_stage
  task_name            = "resolved_hosts"
  object_template      = "${path.module}/indexes/resolved_hosts.pattern.json"
  object_substitutions = {}

  object_type  = "index-pattern"
  object_title = "resolved_hosts:data:read*"
  es_domain = data.aws_ssm_parameter.es_domain.value
}