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

variable "db_user" {
  description = "PostgreSQL DB user"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL DB password"
  type        = string
  sensitive   = true
}

variable "git_repo_url" {
  description = "URL do repositório Git da aplicação."
  type        = string
}

variable "s3_bucket_name" {
  description = "Nome do bucket S3."
  type        = string
}

resource "aws_instance" "app_server" {
  ami           = "ami-0360c520857e3138f"
  instance_type = "t3.micro"
  security_groups = [aws_security_group.app_sg.name]
  iam_instance_profile = "LabInstanceProfile"

  user_data = templatefile("user_data.sh", {
    git_repo_url    = var.git_repo_url
    db_host         = aws_db_instance.postgres_db.address
    db_user         = var.db_user
    db_password     = var.db_password
    db_name         = aws_db_instance.postgres_db.db_name
    s3_bucket_name  = var.s3_bucket_name
    aws_region      = "us-east-1"
  })
  
  tags = {
    Name = "T1-App-Server"
  }
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

resource "aws_security_group" "db_sg" {
  name        = "db_sg"
  description = "Security group para o banco de dados PostgreSQL"

  ingress {
    description     = "Permite acesso da instancia EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  ingress {
    description      = "Permite acesso global"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres_db" {
  identifier           = "t1-app-db"
  allocated_storage    = 10
  engine               = "postgres"
  engine_version       = "17"
  instance_class       = "db.t3.micro"
  db_name              = "t1_app_database"
  username             = var.db_user
  password             = var.db_password
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  allow_major_version_upgrade = true
  publicly_accessible = true
  skip_final_snapshot = true

  tags = {
    Name = "T1-Postgres-DB"
  }
}

resource "aws_s3_bucket" "app_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "T1-App-Storage"
  }
}

resource "aws_s3_bucket_public_access_block" "app_bucket_pab" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "app_server_public_ip" {
  description = "O IP público da instância da aplicação."
  value       = aws_instance.app_server.public_ip
}

output "db_endpoint" {
  description = "O endpoint (host) do banco de dados RDS."
  value       = aws_db_instance.postgres_db.endpoint
}

output "s3_bucket_name" {
  description = "O nome do bucket S3 criado."
  value       = aws_s3_bucket.app_bucket.id
}

