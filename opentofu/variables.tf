variable "aws_region" {
	default = "us-west-2"
	description = "aws-region"
}

variable "vpc_cidr" {
	default = "10.0.0.0/16"
	description = "default cidr range for vpc"
}
