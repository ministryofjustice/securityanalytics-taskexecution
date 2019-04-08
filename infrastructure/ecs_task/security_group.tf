data "aws_ssm_parameter" "vpc_id" {
  name = "/${var.app_name}/${terraform.workspace}/vpc/id"
}

# TODO - probably want to be able to inject a security group for each task
resource "aws_security_group" "task_group" {
  name        = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  description = "Allow all outbound, but no inbound"
  vpc_id      = "${data.aws_ssm_parameter.vpc_id.value}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}
