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
    jwt_issuer     = aws_cognito_user_pool.user_pool.endpoint
    jwt_audience   = aws_cognito_user_pool_client.app_client.id
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

variable "cognito_domain_prefix" {
  description = "Prefixo de domínio globalmente único para o Cognito Hosted UI (ex: t1-construcao-app-123)"
  type        = string
}

resource "aws_cognito_user_pool" "user_pool" {
  name = "t1-app-user-pool"
  auto_verified_attributes = ["email"]

  tags = {
    Name = "T1-User-Pool"
  }
}

resource "aws_cognito_user_group" "admin_group" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Grupo de administradores"
}

resource "aws_cognito_user_group" "user_group" {
  name         = "user"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Grupo de utilizadores padrão"
}

resource "aws_cognito_user_pool_client" "app_client" {
  name = "t1-app-client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows           = ["code"]
  allowed_oauth_scopes          = ["openid", "email", "profile"]

  callback_urls = ["http://localhost:8000/token"]
  logout_urls   = ["http://localhost:8000"]

  supported_identity_providers = ["COGNITO"]

  generate_secret = false
}

resource "aws_cognito_user_pool_domain" "app_domain" {
  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.user_pool.id
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

output "cognito_issuer_url" {
  description = "A URL do Issuer para o JWT (usar como JWT_ISSUER no .env)"
  # O 'endpoint' já vem no formato: https://cognito-idp.[regiao].amazonaws.com/[pool_id]
  value       = aws_cognito_user_pool.user_pool.endpoint
}

output "cognito_app_client_id" {
  description = "O ID do App Client para o JWT (usar como JWT_AUDIENCE no .env)"
  value       = aws_cognito_user_pool_client.app_client.id
}

output "cognito_hosted_ui_url" {
  description = "URL da página de login (Hosted UI) para gerar tokens de teste"
  value       = "https://${aws_cognito_user_pool_domain.app_domain.domain}.auth.us-east-1.amazoncognito.com"
}