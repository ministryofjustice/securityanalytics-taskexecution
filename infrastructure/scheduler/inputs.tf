variable "app_name" {
  type = "string"
}

variable "task_name" {
  type = "string"
}

variable "queue_url" {
  type = "string"
}

variable "queue_arn" {
  type = "string"
}

variable "scan_hosts" {
  type = "list"
}

variable "transient_workspace" {
  type        = "string"
  description = "Used when doing integration tests to make the results buckets created deleteable."
}
