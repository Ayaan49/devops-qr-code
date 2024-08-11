resource "aws_iam_role" "eks_s3_access" {
  name = "eks-s3-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",

        Condition = {
        StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub" : "system:serviceaccount:default:s3-access-sa"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_s3_policy_attachment" {
  role       = aws_iam_role.eks_s3_access.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
