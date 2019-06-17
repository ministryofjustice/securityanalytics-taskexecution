resource "aws_ssm_parameter" "shared_task_code_layer" {
  name        = "/${var.app_name}/${terraform.workspace}/lambda/layers/shared_task_code/arn"
  description = "The arn of the utils lambda layer"
  type        = "String"
  value       = aws_lambda_layer_version.shared_task_code_layer.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}
