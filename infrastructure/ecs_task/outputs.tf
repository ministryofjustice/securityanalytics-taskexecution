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

output "trigger_dead_letter_queue" {
  value = module.taskmodule.trigger_dead_letter_queue
}

output "results_dead_letter_queue" {
  value = module.taskmodule.results_dead_letter_queue
}

output "task_queue_consumer_arn" {
  value = module.taskmodule.task_queue_consumer_arn
}

output "task_queue_consumer_role" {
  value = module.taskmodule.task_queue_consumer_role
}

output "s3_bucket_policy_arn" {
  value = module.taskmodule.s3_bucket_policy_arn
}
output "s3_bucket_policy_doc" {
  value = module.taskmodule.s3_bucket_policy_doc
}
