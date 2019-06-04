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
    docker_hash    = var.docker_hash
    results_bucket = module.taskmodule.results_bucket_arn
    script_hash    = var.sources_hash
  }

  provisioner "local-exec" {
    # # command = "${path.module}/update_docker_image.sh ${var.task_name} ${aws_ecr_repository.repo.repository_url} ${var.docker_dir} ${var.aws_region} ${var.app_name}"
    # #command = "${replace(dirname("${path.module}/update_docker_image.sh"), "/", "\\")} ${var.task_name} ${aws_ecr_repository.repo.repository_url} ${var.docker_dir} ${var.aws_region} ${var.app_name}"
    # command = <<EOF
    #   "${path.module}/update_docker_image.sh" ${var.task_name} ${aws_ecr_repository.repo.repository_url} ${var.docker_dir} ${var.aws_region} ${var.app_name}
    # EOF
    command     = ".\\update_docker_image.sh ${var.task_name} ${aws_ecr_repository.repo.repository_url} ${path.root}/${var.docker_dir} ${var.aws_region} ${var.app_name}"
    working_dir = "${path.module}"
  }
}

