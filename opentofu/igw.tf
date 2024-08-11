resource "aws_internet_gateway" "my-igw" {
	vpc_id = aws_vpc.new.id

	tags = {
		Name = "my-igw"
	}
}
