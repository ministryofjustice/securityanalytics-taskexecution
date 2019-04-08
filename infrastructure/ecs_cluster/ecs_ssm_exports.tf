resource "aws_ssm_parameter" "ecs_cluster" {
  name        = "/${var.app_name}/${terraform.workspace}/ecs/cluster"
  description = "The ECS cluster's id"
  type        = "StringList"
  value       = "${aws_ecs_cluster.scanning_cluster.id}"
  overwrite   = "true"

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}
