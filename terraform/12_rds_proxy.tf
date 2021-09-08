resource "aws_db_proxy" "production" {
    name                   = "${var.ecs_cluster_name}-rds-proxy"
    debug_logging          = false
    engine_family          = "POSTGRESQL"
    idle_client_timeout    = 1800
    require_tls            = true
    role_arn               = aws_iam_role.rds-proxy-role.arn
    vpc_security_group_ids = [aws_security_group.rds-proxy.id]
    vpc_subnet_ids         = [aws_subnet.private-subnet-1.id, aws_subnet.private-subnet-2.id]

    auth {
        auth_scheme = "SECRETS"
        iam_auth    = "DISABLED"
        secret_arn  = aws_secretsmanager_secret.rds-secret.arn
    }
}

resource "aws_db_proxy_default_target_group" "production" {
    db_proxy_name = aws_db_proxy.production.name

    connection_pool_config {
        connection_borrow_timeout = 120
        max_connections_percent = 100
        max_idle_connections_percent = 50
    }
}

resource "aws_db_proxy_target" "production" {
    db_cluster_identifier = aws_rds_cluster.production.id
    db_proxy_name         = aws_db_proxy.production.name
    target_group_name     = aws_db_proxy_default_target_group.production.name
    depends_on            = [aws_rds_cluster_instance.production]
}

resource "aws_db_proxy_endpoint" "production-ro" {
    db_proxy_name          = aws_db_proxy.production.name
    db_proxy_endpoint_name = "${var.ecs_cluster_name}-rds-proxy-endpoint-ro"
    vpc_subnet_ids         = [aws_subnet.private-subnet-1.id, aws_subnet.private-subnet-2.id]
    target_role            = "READ_ONLY"
}

resource "aws_db_proxy_endpoint" "production-rw" {
    db_proxy_name          = aws_db_proxy.production.name
    db_proxy_endpoint_name = "${var.ecs_cluster_name}-rds-proxy-endpoint-rw"
    vpc_subnet_ids         = [aws_subnet.private-subnet-1.id, aws_subnet.private-subnet-2.id]
    target_role            = "READ_WRITE"
}
