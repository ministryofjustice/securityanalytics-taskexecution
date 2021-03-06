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
  value = module.taskmodule.trigger_role_arn
}

output "results_parser" {
  value = module.taskmodule.results_parser
}

output "trigger_dead_letter_queue" {
  value = module.taskmodule.trigger_dead_letter_queue
}

output "results_dead_letter_queue" {
  value = module.taskmodule.results_dead_letter_queue
}

output "trigger_role_name" {
  value = module.taskmodule.trigger_role_name
}

output "trigger_role_arn" {
  value = module.taskmodule.trigger_role_arn
}
