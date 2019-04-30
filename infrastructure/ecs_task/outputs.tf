output "results_bucket_arn" {
  value = "${aws_s3_bucket.results.arn}"
}

output "results_bucket_id" {
  value = "${aws_s3_bucket.results.id}"
}

output "task_queue_consumer" {
  value = "${aws_iam_role.task_trigger_role.arn}"
}

output "task_queue_url" {
  value = "${aws_sqs_queue.trigger_queue.id}"
}

output "task_queue" {
  value = "${aws_sqs_queue.trigger_queue.arn}"
}
