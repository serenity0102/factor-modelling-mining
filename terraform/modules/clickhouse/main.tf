resource "aws_security_group" "clickhouse" {
  name        = "${var.project_name}-clickhouse-sg"
  description = "Security group for Clickhouse"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 8123
    to_port     = 8123
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP interface"
  }

  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Native interface"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-clickhouse-sg"
    Environment = var.environment
  }
}

resource "aws_instance" "clickhouse" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_ids[0]
  vpc_security_group_ids = [aws_security_group.clickhouse.id]
  key_name               = var.key_name
  
  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    # Install Clickhouse
    sudo yum update -y
    sudo yum install -y curl
    
    # Install Clickhouse
    curl https://clickhouse.com/ | sh
    sudo clickhouse start
    
    # Configure Clickhouse to listen on all interfaces
    sudo sed -i 's/<listen_host>::1/<listen_host>0.0.0.0/g' /etc/clickhouse-server/config.xml
    sudo systemctl restart clickhouse-server
  EOF

  tags = {
    Name        = "${var.project_name}-clickhouse"
    Environment = var.environment
  }
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
