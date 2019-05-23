locals {
  scheduler_zip = "../.generated/${var.app_name}-scheduler.zip"
}

data "external" "nmap_zip" {
  program = [
    "python",
    "../shared_code/python/package_lambda.py",
    "${local.scheduler_zip}",
    "${path.module}/packaging.config.json",
    "../Pipfile.lock",
  ]
}
