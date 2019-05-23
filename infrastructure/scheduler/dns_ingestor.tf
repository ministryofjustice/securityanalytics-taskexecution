resource "aws_lambda_function" "ingest_dns" {

  function_name    = "${terraform.workspace}-${var.app_name}-ingest-dns"
  handler          = "ingest_dns.ingest_dns.ingest_dns"
  role             = "${aws_iam_role.dns_ingestor.arn}"
  runtime          = "python3.7"
  filename         = "${local.scheduler_zip}"
  source_code_hash = "${data.external.nmap_zip.result.hash}"

  layers = [
    "${data.aws_ssm_parameter.utils_layer.value}",
  ]

  # We have to rate limit dns requests, so there are sleeps in the code
  # and this lambda takes quite a lot of time ~2mins (setting over double for safety)
  timeout = "${5 * 60}"

  environment {
    variables = {
      REGION    = "${var.aws_region}"
      STAGE     = "${terraform.workspace}"
      APP_NAME  = "${var.app_name}"
    }
  }

  tags = {
    workspace = "${terraform.workspace}"
    app_name  = "${var.app_name}"
  }
}


data "aws_iam_policy_document" "lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dns_ingestor" {
  name               = "${terraform.workspace}-${var.app_name}-dns-ingestor"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_trust.json}"

  # TODO needs access to dynamodb, sns, assume role, and route53

  tags {
    app_name  = "${var.app_name}"
    workspace = "${terraform.workspace}"
  }
}