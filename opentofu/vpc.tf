resource "aws_vpc" "new" {
	cidr_block = var.vpc_cidr

	tags = {
	  Name = "new"
	}

}
