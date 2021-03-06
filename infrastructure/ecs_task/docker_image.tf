resource "aws_ecr_repository" "repo" {
  name = "${terraform.workspace}-${var.app_name}-${var.task_name}-repo"

  tags = {
    task_name = var.task_name
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}

resource "null_resource" "build_image" {
  # TODO, triggers not working properly, always creating new image
  triggers = {
    # hash tags make sure we redeploy on a change
    docker_hash    = var.docker_combined_hash
    results_bucket = module.taskmodule.results_bucket_arn
  }

  provisioner "local-exec" {
    command = "${path.cwd}/${path.module}/update_docker_image.sh ${var.task_name} ${aws_ecr_repository.repo.repository_url} ${dirname("${path.cwd}/${var.docker_file}")} ${var.aws_region} ${var.app_name}"
  }
}

