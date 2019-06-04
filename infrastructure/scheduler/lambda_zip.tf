locals {
  scheduler_zip = "../.generated/${var.app_name}-scheduler.zip"
}

data "external" "scheduler_zip" {
  program = [
    "python",
    "../shared_code/python/package_lambda.py",
    "-x", # will include the normally excluded packages
    local.scheduler_zip,
    "${path.module}/packaging.config.json",
    "../Pipfile.lock",
  ]
}

