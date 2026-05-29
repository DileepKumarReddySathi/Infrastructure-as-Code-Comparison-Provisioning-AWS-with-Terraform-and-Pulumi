# Primary S3 bucket with versioning
resource "aws_s3_bucket" "main_app_bucket" {
  bucket_prefix = "app-bucket-tf-"
}

resource "aws_s3_bucket_versioning" "main_app_bucket_versioning" {
  bucket = aws_s3_bucket.main_app_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Dynamic Resource Creation for logging buckets
locals {
  environments = toset(["dev", "staging", "prod"])
}

resource "aws_s3_bucket" "logs" {
  for_each = local.environments
  bucket   = "myapp-logs-${each.key}"
  tags = {
    Environment = each.value
  }
}
