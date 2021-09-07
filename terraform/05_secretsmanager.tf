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
        "host"                 = aws_db_instance.production.address
        "port"                 = 5432
        "dbInstanceIdentifier" = aws_db_instance.production.id
    })
}