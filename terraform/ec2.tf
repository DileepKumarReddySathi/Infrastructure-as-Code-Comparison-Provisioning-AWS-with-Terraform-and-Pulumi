# IAM Role for EC2 to access S3
resource "aws_iam_role" "ec2_s3_role" {
  name = "ec2-s3-access-role-tf"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for S3 PutObject
resource "aws_iam_role_policy" "s3_put_policy" {
  name = "s3-put-policy-tf"
  role = aws_iam_role.ec2_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = "${aws_s3_bucket.main_app_bucket.arn}/*"
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "s3_profile" {
  name = "ec2-s3-profile-tf"
  role = aws_iam_role.ec2_s3_role.name
}

# Security Group to allow HTTP and SSH
resource "aws_security_group" "web_sg" {
  name        = "web-sg-tf"
  description = "Allow HTTP and SSH inbound traffic"
  vpc_id      = aws_vpc.app_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "app_server" {
  ami                    = "ami-0c55b159cbfafe1f0" # Using Amazon Linux 2023 base provided in prompt
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.s3_profile.name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              service docker start
              usermod -a -G docker ec2-user
              EOF

  tags = {
    Name = "app-server-tf"
  }
}
