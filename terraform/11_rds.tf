resource "aws_db_subnet_group" "production" {
    name       = "private-subnet-group"
    subnet_ids = [aws_subnet.private-subnet-1.id, aws_subnet.private-subnet-2.id]
}

# resource "aws_db_instance" "production" {
#     identifier              = "pagenow-user-api-production"
#     name                    = var.rds_db_name
#     username                = var.rds_username
#     password                = var.rds_password
#     port                    = "5432"
#     engine                  = "postgres"
#     engine_version          = "11.5"
#     instance_class          = var.rds_instance_class
#     allocated_storage       = "20"
#     storage_encrypted       = false
#     vpc_security_group_ids  = [aws_security_group.rds.id]
#     db_subnet_group_name    = aws_db_subnet_group.production.name
#     multi_az                = false
#     storage_type            = "gp2"
#     publicly_accessible     = false
#     backup_retention_period = 7
#     skip_final_snapshot     = true
# }

resource "aws_rds_cluster" "production" {
    cluster_identifier      = "${var.ecs_cluster_name}-rds-cluster"
    engine                  = var.rds_engine
    engine_version          = var.rds_engine_version
    database_name           = var.rds_db_name
    master_username         = var.rds_username
    master_password         = var.rds_password
    port                    = var.rds_port
    db_subnet_group_name    = aws_db_subnet_group.production.name
    backup_retention_period = 5
    preferred_backup_window = "07:00-09:00"
    vpc_security_group_ids  = [aws_security_group.rds.id]
    skip_final_snapshot     = true
}

resource "aws_rds_cluster_instance" "production" {
    count                = 2
    identifier           = "${var.ecs_cluster_name}-rds-instance-${count.index}"
    apply_immediately    = true
    cluster_identifier   = aws_rds_cluster.production.id
    instance_class       = var.rds_instance_class
    engine               = var.rds_engine
    engine_version       = var.rds_engine_version
    publicly_accessible  = false
    db_subnet_group_name = aws_db_subnet_group.production.name
}
