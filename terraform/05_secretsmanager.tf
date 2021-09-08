resource "aws_secretsmanager_secret" "rds-secret" {
    name_prefix = "rds-proxy-secret"
    recovery_window_in_days = 7
    description = "Secret for RDS Proxy"
}

resource "aws_secretsmanager_secret_version" "rds-secret-version" {
    secret_id     = aws_secretsmanager_secret.rds-secret.id
    secret_string = jsonencode({
        "username"             = var.rds_username
        "password"             = var.rds_password
        "engine"               = "postgres"
        "host"                 = aws_rds_cluster.production.endpoint
        "port"                 = var.rds_port
        "dbClusterIdentifier"  = aws_rds_cluster.production.id
    })
}