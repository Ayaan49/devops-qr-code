resource "aws_iam_policy" "eks_s3_access_policy" {
  name        = "eks-s3-access-policy"
  policy      = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::new-bucket666"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::new-bucket666/qr_codes/*"
        },
		{
    		"Effect": "Allow",
    		"Action": "s3:PutObjectAcl",
    		"Resource": "arn:aws:s3:::new-bucket666/qr_codes/*"
		}

			]
}
EOF
}

resource "aws_iam_role" "eks_s3_access" {
  name = "eks-s3-access"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${aws_iam_openid_connect_provider.eks.arn}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub": "system:serviceaccount:default:s3-access-sa"
        }
      }
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "eks_s3_access_policy_attachment" {
  role       = aws_iam_role.eks_s3_access.name
  policy_arn = aws_iam_policy.eks_s3_access_policy.arn
}
