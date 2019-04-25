output "results_bucket_arn" {
  value = "${aws_s3_bucket.results.arn}"
}

output "results_bucket_id" {
  value = "${aws_s3_bucket.results.id}"
}
