resource "aws_db_proxy" "production" {
    name                   = "production"
    debug_logging          = false
    engine_family          = "POSTGRESQL"
    idle_client_timeout    = 1800
    require_tls            = true
    role_arn               = aws_iam_role.rds-proxy-role.arn
    vpc_security_group_ids = [aws_security_group.rds-proxy.id]
    vpc_subnet_ids         = [aws_subnet.private-subnet-1.id, aws_subnet.private-subnet-2.id]

    auth {
        auth_scheme = "SECRETS"
        iam_auth    = "REQUIRED"
        secret_arn  = aws_secretsmanager_secret.rds-secret.arn
    }
}

resource "aws_db_proxy_default_target_group" "rds-proxy-target-group" {
    db_proxy_name = aws_db_proxy.production.name

    connection_pool_config {
        connection_borrow_timeout = 120
        max_connections_percent = 95
    }
}

resource "aws_db_proxy_target" "rds-proxy-target" {
    db_instance_identifier = aws_db_instance.production.id
    db_proxy_name          = aws_db_proxy.production.name
    target_group_name      = aws_db_proxy_default_target_group.rds-proxy-target-group.name
}

