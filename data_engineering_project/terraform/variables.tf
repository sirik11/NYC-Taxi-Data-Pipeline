variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket used for storing raw and processed taxi data"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EMR cluster EC2 instances"
  type        = string
}

variable "db_security_group_id" {
  description = "Security group ID allowing access to the RDS instance"
  type        = string
}

variable "rds_db_name" {
  description = "Database name for the RDS PostgreSQL instance"
  type        = string
  default     = "taxidb"
}

variable "rds_username" {
  description = "Master username for the RDS PostgreSQL instance"
  type        = string
}

variable "rds_password" {
  description = "Master password for the RDS PostgreSQL instance"
  type        = string
  sensitive   = true
}