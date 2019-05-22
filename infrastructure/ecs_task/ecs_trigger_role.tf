data "aws_caller_identity" "account" {}

data "aws_iam_policy_document" "ecs_trigger_policy" {
  statement {
    effect    = "Allow"
    actions   = ["ecs:RunTask"]
    resources = ["${aws_ecs_task_definition.task.arn}"]
  }

  # To allow the trigger to pass the execution role to ecs to assume when running the task
  statement {
    effect  = "Allow"
    actions = ["iam:PassRole"]

    resources = [
      "${data.aws_iam_role.ecs_exec_role.arn}",
      "${aws_iam_role.task_role.arn}",
    ]
  }
}

resource "aws_iam_policy" "ecs_trigger_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}-ecs-trigger"
  policy = "${data.aws_iam_policy_document.ecs_trigger_policy.json}"
}

resource "aws_iam_role_policy_attachment" "ecs_trigger_policy" {
  role       = "${module.taskmodule.trigger_role_name}"
  policy_arn = "${aws_iam_policy.ecs_trigger_policy.arn}"
}
