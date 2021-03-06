# ALB Security Group (Traffic Internet -> ALB)
resource "aws_security_group" "load-balancer" {
    name        = "load_balancer_security_group"
    description = "Controls access to the ALB"
    vpc_id      = aws_vpc.production-vpc.id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 443
        to_port     = 443
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

# ECS Security group (traffic ALB -> ECS, ssh -> ECS)
resource "aws_security_group" "ecs" {
    name        = "ecs_security_group"
    description = "Allows inbound access from the ALB only"
    vpc_id      = aws_vpc.production-vpc.id

    ingress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        security_groups = [aws_security_group.load-balancer.id]
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

# RDS Security Group (traffic ECS -> RDS Proxy)
resource "aws_security_group" "rds-proxy" {
    name        = "rds-proxy-security-group"
    description = "Allows inbound access from ECS only"
    vpc_id      = aws_vpc.production-vpc.id

    ingress {
        protocol        = "tcp"
        from_port       = "5432"
        to_port         = "5432"
        security_groups = [aws_security_group.ecs.id]
    }

    egress {
        protocol    = "-1"
        from_port   = 0
        to_port     = 0
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# RDS Security Group (traffic RDS Proxy -> RDS)
resource "aws_security_group" "rds" {
    name        = "rds-security-group"
    description = "Allows inbound access from RDS Proxy only"
    vpc_id      = aws_vpc.production-vpc.id

    ingress {
        protocol        = "tcp"
        from_port       = "5432"
        to_port         = "5432"
        security_groups = [aws_security_group.rds-proxy.id, aws_security_group.ecs.id]
    }

    egress {
        protocol    = "-1"
        from_port   = 0
        to_port     = 0
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# Security group that allows ssh from the internet
resource "aws_security_group" "allow-ssh" {
    vpc_id      = aws_vpc.production-vpc.id
    name        = "allow-ssh"
    description = "Security group that allows ssh and all egress traffic"

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "allow-ssh"
    }
}