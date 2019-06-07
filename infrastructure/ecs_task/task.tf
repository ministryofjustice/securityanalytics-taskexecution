// Import the standard execution role AWS generate for us
data "aws_iam_role" "ecs_exec_role" {
  name = "ecsTaskExecutionRole"
}

data "template_file" "task" {
  template = file("${path.module}/service.json")

  vars = {
    stage        = terraform.workspace
    app_name     = var.app_name
    task_name    = var.task_name
    aws_region   = var.aws_region
    docker_image = aws_ecr_repository.repo.repository_url
    // hash tags make sure we update the task on a change
    docker_hash    = var.docker_hash
    results_bucket = module.taskmodule.results_bucket_arn
    sources_hash   = var.sources_hash
  }
}

resource "aws_cloudwatch_log_group" "task_logs" {
  name = "/aws/ecs/${terraform.workspace}/${var.app_name}/${var.task_name}"
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${terraform.workspace}-${var.app_name}-${var.task_name}"
  task_role_arn            = aws_iam_role.task_role.arn
  execution_role_arn       = data.aws_iam_role.ecs_exec_role.arn
  network_mode             = "awsvpc"
  container_definitions    = data.template_file.task.rendered
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory

  tags = {
    task_name = var.task_name
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

module "taskmodule" {
  source                        = "../task"
  app_name                      = var.app_name
  aws_region                    = var.aws_region
  task_name                     = var.task_name
  subscribe_elastic_to_notifier = var.subscribe_elastic_to_notifier
  account_id                    = var.account_id
  ssm_source_stage              = var.ssm_source_stage
  transient_workspace           = var.transient_workspace
  use_xray = var.use_xray
  results_parser_arn = var.results_parser_arn
}

