terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "app_sg" {
  name        = "app_sg"
  description = "Security group for T1 app"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8080
    to_port     = 8080
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

resource "aws_instance" "app_server" {
  ami           = "ami-0360c520857e3138f"
  instance_type = "t3.micro"
  security_groups = [aws_security_group.app_sg.name]

  tags = {
    Name = "T1-App-Server"
  }

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update
    sudo apt install -y git curl python3.12 python3.12-venv python3.12-dev python3-pip docker.io
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo usermod -aG docker ubuntu
    export PATH="$HOME/.local/bin:$PATH"
    curl -sSL https://install.python-poetry.org | python3.12 -
    cd /home/ubuntu
    if [ -d "T1_construcao" ]; then
      cd T1_construcao
      git pull
    else
      git clone https://github.com/Pedro05Souza/T1_construcao.git
      cd T1_construcao
    fi
    cp .env.template .env || true
    /home/ubuntu/.local/bin/poetry install
    sudo docker compose up -d
  EOF
}
