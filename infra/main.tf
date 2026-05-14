terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1" # Change to your preferred free-tier region
}

# Default VPC Data Sources
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group
resource "aws_security_group" "k3s_sg" {
  name        = "edunexus-k3s-sg"
  description = "Allow HTTP, HTTPS, and SSH"
  vpc_id      = data.aws_vpc.default.id

  # Allow HTTP for Web API
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH to install K3s and ArgoCD (Consider restricting to your personal IP!)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow the server to talk to the internet (to download Docker images)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "k3s_server" {
  ami           = "ami-0c7217cdde317cfec" 
  instance_type = "t2.micro"              

  vpc_security_group_ids = [aws_security_group.k3s_sg.id]

  tags = {
    Name = "EduNexus-K3s-ArgoCD"
  }

  user_data = <<-EOF
              #!/bin/bash
              curl -sfL https://get.k3s.io | sh -
              
              sleep 15
              export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
              chmod 644 /etc/rancher/k3s/k3s.yaml

              kubectl create namespace argocd
              kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
              
              kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'
              EOF
}

output "server_public_ip" {
  description = "Public IP"
  value       = aws_instance.k3s_server.public_ip
}

# ECR Repository
resource "aws_ecr_repository" "edunexus_repo" {
  name                 = "edunexus"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.edunexus_repo.repository_url
}
