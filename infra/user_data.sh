#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y git docker.io

systemctl start docker
systemctl enable docker
usermod -a -G docker ubuntu

DOCKER_CONFIG=$${DOCKER_CONFIG:-/usr/local/lib/docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

git clone ${git_repo_url} /home/ubuntu/app
cd /home/ubuntu/app

cat > .env <<EOF
DATABASE_HOST="${db_host}"
DATABASE_USER="${db_user}"
DATABASE_PASSWORD="${db_password}"
DATABASE_PORT="5432"
DATABASE_NAME="${db_name}"

S3_BUCKET_NAME="${s3_bucket_name}"
AWS_REGION="${aws_region}"
PYTHONUNBUFFERED=1
PYTHONPATH="/app/src"
EOF

chown -R ubuntu:ubuntu /home/ubuntu/app

su - ubuntu -c "cd /home/ubuntu/app && docker compose up --build -d"