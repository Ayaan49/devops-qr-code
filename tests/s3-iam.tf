data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::new-bucket666",
      "arn:aws:s3:::new-bucket666/qr_codes/*"
    ]
  }
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "s3-access-policy"
  path        = "/"
  description = "S3 access policy for QR code generation"
  policy      = data.aws_iam_policy_document.s3_access_policy.json
}

resource "aws_iam_role" "s3_access_role" {
  name = "s3-access-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        }
        Condition = {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub" : "system:serviceaccount:default:s3-access-sa"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access_attach" {
  policy_arn = aws_iam_policy.s3_access_policy.arn
  role       = aws_iam_role.s3_access_role.name
}
