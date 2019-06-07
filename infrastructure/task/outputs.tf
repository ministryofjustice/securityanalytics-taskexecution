output "results_bucket_arn" {
  value = aws_s3_bucket.results.arn
}

output "results_bucket_id" {
  value = aws_s3_bucket.results.id
}

output "task_queue_consumer_arn" {
  value = aws_iam_role.task_trigger_role.arn
}

output "task_queue_consumer_role" {
  value = aws_iam_role.task_trigger_role.name
}

output "trigger_role_name" {
  value = aws_iam_role.task_trigger_role.name
}

output "results_parser" {
  value = aws_iam_role.results_parse_role.arn
}

output "task_queue_url" {
  value = aws_sqs_queue.trigger_queue.id
}

output "task_queue" {
  value = aws_sqs_queue.trigger_queue.arn
}

output "task_trigger_policy_arn" {
  value = aws_iam_policy.task_trigger_policy.arn
}

output "s3_bucket_policy_arn" {
  value = aws_iam_policy.s3_bucket_access_policy.arn
}

output "s3_bucket_policy_doc" {
  value = aws_iam_policy.s3_bucket_access_policy.policy
}

output "dead_letter_queue" {
  value = module.dead_letters.arn
}

