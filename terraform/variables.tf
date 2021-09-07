# Core
variable "region" {
    description = "The AWS region to create resources in."
    default     = "us-west-2"
}

# Networking
variable "public_subnet_1_cidr" {
    description = "CIDR Block for Public Subnet 1"
    default     = "10.0.1.0/24"
}
variable "public_subnet_2_cidr" {
    description = "CIDR Block for Public Subnet 2"
    default     = "10.0.2.0/24"
}
variable "private_subnet_1_cidr" {
    description = "CIDR Block for Private Subnet 1"
    default     = "10.0.3.0/24"
}
variable "private_subnet_2_cidr" {
    description = "CIDR Block for Private Subnet 2"
    default     = "10.0.4.0/24"
}
# variable "presence_redis_subnet_1_cidr" {
#     description = "CIDR Block for Presence Redis Subnet 1"
#     default     = "10.0.5.0/24"
# }
# variable "presence_redis_subnet_2_cidr" {
#     description = "CIDR Block for Presence Redis Subnet 2"
#     default     = "10.0.6.0/24"
# }
# variable "presence_lambda_subnet_1_cidr" {
#     description = "CIDR Block for Presence Lambda Subnet 1"
#     default     = "10.0.7.0/24"
# }
# variable "presence_lambda_subnet_2_cidr" {
#     description = "CIDR Block for Presence Lambda Subnet 2"
#     default     = "10.0.8.0/24"
# }
# variable "presence_redis_subnet_name" {
#     description = "Name of Presence Redis Subnet"
#     default     = "Presence Redis"
# }
# variable "presence_lambda_subnet_name" {
#     description = "Name of Presence Lambda Subnet"
#     default     = "Presence Lambda"
# }
variable "availability_zones" {
    description = "Availability zones"
    type        = list(string)
    default     = ["us-west-2a", "us-west-2b"]
}

# Load Balancer
variable "health_check_path" {
    description = "Health check path for the default target group"
    default     = "/ping"
}

# Logs
variable "log_retention_in_days" {
    default = 30
}

# Key Pair
variable "ssh_pubkey_file" {
    description = "Path to an SSH public key"
    default     = "~/.ssh/id_rsa.pub"
}

# ECS
variable "ecs_cluster_name" {
    description = "Name of the ECS cluster"
    default     = "user-api-production"
}
variable "amis" {
    description = "Which AMI to spawn"
    default = {
        us-west-2 = "ami-06cb61a83c506fe88"
    }
}
variable "instance_type" {
    default = "t2.micro"
}
variable "docker_image_url_pagenow_user_api" {
    description = "Docker image to run in the ECS cluster"
    default     = "257206538165.dkr.ecr.us-west-2.amazonaws.com/pagenow-user-api:latest"
}
variable "app_count" {
    description = "Number of Docker containers to run"
    default     = 1
}
# variable "allowed_hosts" {
#   description = "Domain name for allowed hosts"
#   default     = "YOUR DOMAIN NAME"
# }

# Auto Scaling Group
variable "autoscale_min" {
    description = "Minimum autoscale (number of EC2)"
    default     = "1"
}
variable "autoscale_max" {
    description = "Maximum autoscale (number of EC2)"
    default     = "10"
}
variable "autoscale_desired" {
    description = "Desired autoscale (number of EC2)"
    default     = "2"
}

# RDS
variable "rds_db_name" {
    description = "RDS database name"
    default     = "core_db"
}
variable "rds_username" {
    description = "RDS database username"
    default     = "ylee"
}
variable "rds_password" {
    description = "RDS database password"
}
variable "rds_instance_class" {
    description = "RDS instance type"
    default     = "db.t2.micro"
}

# Domain
# variable "certificate_arn" {
#   description = "AWS Certificate Manager ARN for validated domain"
#   default     = "YOUR ARN"
# }