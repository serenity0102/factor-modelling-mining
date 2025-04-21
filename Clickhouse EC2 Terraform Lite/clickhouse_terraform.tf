provider "aws" {
  region  = "us-east-1"
  profile = "kenchowt+eks-auto-Admin"
}

# Create AWS Secret for ClickHouse credentials
resource "aws_secretsmanager_secret" "clickhouse_credentials" {
  name_prefix = "clickhouse/password-"    # Uses prefix for unique names
  description = "ClickHouse database credentials"
  
  tags = {
    Environment = var.environment
    Project     = "ClickHouse"
    ManagedBy   = "Terraform"
  }
}

# Define variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}


# Create IAM role for EC2 to access Secrets Manager
resource "aws_iam_role" "ec2_role" {
  name = "clickhouse-ec2-role"
  
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

  tags = {
    Environment = var.environment
    Project     = "ClickHouse"
    ManagedBy   = "Terraform"
  }
}

# Create custom policy for Secrets Manager access
resource "aws_iam_policy" "secrets_access" {
  name = "clickhouse-secrets-access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [aws_secretsmanager_secret.clickhouse_credentials.arn]
      }
    ]
  })
}

# Attach secrets policy to the IAM role
resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# Create instance profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "clickhouse-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Create security group
resource "aws_security_group" "clickhouse_sg" {
  name_prefix = "clickhouse-sg-"
  description = "Security group for ClickHouse server"
  vpc_id      = "vpc-0271b7be7b94a01af"
  
  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
    description = "SSH access"
  }
  
  # ClickHouse native interface
  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Restricted to internal network
    description = "ClickHouse native protocol"
  }
  
  # ClickHouse HTTP interface
  ingress {
    from_port   = 8123
    to_port     = 8123
    protocol    = "tcp" 
    cidr_blocks = ["10.0.0.0/8"]  # Restricted to internal network
    description = "ClickHouse HTTP interface"
  }
  
  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "clickhouse-sg"
    Environment = var.environment
    Project     = "ClickHouse"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create EC2 instance
resource "aws_instance" "clickhouse_server" {
  ami                    = "ami-071226ecf16aa7d96"
  instance_type          = "m6i.4xlarge"
  key_name               = "vriginia-ec2-key"
  vpc_security_group_ids = [aws_security_group.clickhouse_sg.id]
  subnet_id              = "subnet-0cad1d92f48292ed6"
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  ebs_optimized          = true
  
  root_block_device {
    volume_size           = 1000
    volume_type           = "gp3"
    iops                  = 16000
    throughput           = 1000
    encrypted            = true
    delete_on_termination = true
    
    tags = {
      Name = "clickhouse-data"
    }
  }
  
  user_data = file("clickhouse_userdata_al2023.sh")
  
  tags = {
    Name        = "clickhouse-server"
    Environment = var.environment
    Project     = "ClickHouse"
    ManagedBy   = "Terraform"
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"  # Enforce IMDSv2
  }

  monitoring = true  # Enable detailed monitoring

  # Lifecycle block removed to allow terraform destroy
}

# Output the instance details
output "instance_id" {
  value = aws_instance.clickhouse_server.id
}

output "private_ip" {
  value = aws_instance.clickhouse_server.private_ip
}

output "private_dns" {
  value = aws_instance.clickhouse_server.private_dns
}
