resource "aws_ecs_cluster" "scanning_cluster" {
  name = "${terraform.workspace}-${var.app_name}-scanning-cluster"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

