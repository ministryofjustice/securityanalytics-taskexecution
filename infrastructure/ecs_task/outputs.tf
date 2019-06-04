output "task_role_name" {
  value = aws_iam_role.task_role.name
}

output "task_queue_url" {
  value = module.taskmodule.task_queue_url
}

output "task_queue" {
  value = module.taskmodule.task_queue
}

output "results_bucket_arn" {
  value = module.taskmodule.results_bucket_arn
}

output "results_bucket_id" {
  value = module.taskmodule.results_bucket_id
}

output "task_queue_consumer" {
  value = module.taskmodule.task_queue_consumer_arn
}

output "results_parser" {
  value = module.taskmodule.results_parser
}

