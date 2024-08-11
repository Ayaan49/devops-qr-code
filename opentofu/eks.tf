resource "aws_iam_role" "andromeda" {

	name = "eks-cluster-andromeda"

	  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY

}

resource "aws_iam_role_policy_attachment" "andromeda-AmazonEKSClusterPolicy" {
	policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
	role = aws_iam_role.andromeda.name

}

resource "aws_eks_cluster" "andromeda" {
	name = "andromeda"
	role_arn = aws_iam_role.andromeda.arn

	 vpc_config {
    subnet_ids = [
      aws_subnet.private-us-west-2a.id,
      aws_subnet.private-us-west-2b.id,
      aws_subnet.public-us-west-2a.id,
      aws_subnet.public-us-west-2b.id
    ]
  }

  depends_on = [aws_iam_role_policy_attachment.andromeda-AmazonEKSClusterPolicy]

}
