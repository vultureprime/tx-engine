terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

variable "var" {
  type = map(string)
  default = {
    bucket_raw = "tf-op-log-raw"
    bucket_result = "tf-op-log-result"
    glue_database = "op-logs-databse"
    glue_crawler = "op-raw-crawler"
    athena_workgroup = "op-workgroup"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "aws_glue_service_role" {
  name = "AWSGlueServiceRole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_glue_service_policy" {
  role       = aws_iam_role.aws_glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_s3_bucket" "bucket" {
  bucket = var.var.bucket_raw
}
resource "aws_s3_bucket" "bucket_result" {
  bucket = var.var.bucket_result
}
output "name" {
  value = aws_s3_bucket.bucket.arn
}
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.bucket.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : "*",
        "Action" : "*",
        "Resource" : "${aws_s3_bucket.bucket.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "access_block" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}


resource "aws_glue_catalog_database" "example" {
  name =  var.var.glue_database
}


resource "aws_glue_crawler" "catalog_crawler" {
  depends_on = [aws_s3_bucket.bucket]
  database_name = aws_glue_catalog_database.example.name
  name          = var.var.glue_crawler
  role          = aws_iam_role.aws_glue_service_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.bucket.bucket}"
  }

  table_prefix = "tf"
  
  schema_change_policy {
    delete_behavior = "LOG"
  }
}

resource "aws_athena_workgroup" "example" {
  name = var.var.athena_workgroup

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.bucket_result.bucket}/"
    }
  }
}