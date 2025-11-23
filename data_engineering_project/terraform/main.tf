terraform {
  required_version = ">= 1.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "taxi_data" {
  bucket = var.s3_bucket_name
  force_destroy = true
  tags = {
    Name        = "taxi-data-bucket"
    Environment = "dev"
  }
}

# Example EMR cluster to process large datasets with Spark
resource "aws_emr_cluster" "taxi_cluster" {
  name          = "taxi-data-emr"
  release_label = "emr-6.12.0"
  applications  = ["Spark"]
  service_role  = aws_iam_role.emr_service.arn
  ec2_attributes {
    instance_profile = aws_iam_instance_profile.emr_ec2_profile.arn
    subnet_id        = var.subnet_id
  }
  master_instance_type = "m5.xlarge"
  core_instance_type   = "m5.xlarge"
  core_instance_count  = 2
  bootstrap_action {
    path = "s3://"${aws_s3_bucket.taxi_data.bucket}"/bootstrap.sh"
  }
  tags = {
    Name = "taxi-emr"
  }
}

# Example RDS PostgreSQL database for warehousing
resource "aws_db_instance" "taxi_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  db_name              = var.rds_db_name
  username             = var.rds_username
  password             = var.rds_password
  skip_final_snapshot  = true
  publicly_accessible  = false
  vpc_security_group_ids = [var.db_security_group_id]
  tags = {
    Name = "taxi-rds"
  }
}

# IAM role for EMR service
resource "aws_iam_role" "emr_service" {
  name = "emr_service_role"
  assume_role_policy = data.aws_iam_policy_document.emr_service_assume.json
}

data "aws_iam_policy_document" "emr_service_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["elasticmapreduce.amazonaws.com"]
    }
  }
}

# IAM instance profile for EMR EC2 instances
resource "aws_iam_role" "emr_ec2_role" {
  name = "emr_ec2_role"
  assume_role_policy = data.aws_iam_policy_document.emr_ec2_assume.json
}

data "aws_iam_policy_document" "emr_ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_instance_profile" "emr_ec2_profile" {
  name = "emr_ec2_profile"
  role = aws_iam_role.emr_ec2_role.name
}