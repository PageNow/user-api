# Production ECS
resource "aws_ecs_cluster" "production" {
    name = "${var.ecs_cluster_name}-cluster"
}

resource "aws_launch_configuration" "ecs" {
    name                        = "${var.ecs_cluster_name}-cluster"
    image_id                    = lookup(var.amis, var.region)
    instance_type               = var.prod_instance_type
    security_groups             = [aws_security_group.ecs.id]
    iam_instance_profile        = aws_iam_instance_profile.ecs.name
    key_name                    = aws_key_pair.production.key_name
    associate_public_ip_address = true
    user_data                   = "#!/bin/bash\necho ECS_CLUSTER='${var.ecs_cluster_name}-cluster' > /etc/ecs/ecs.config"
}

data "template_file" "app" {
    template = file("templates/user-api.json.tpl")

    vars = {
        docker_image_url_pagenow_user_api = var.docker_image_url_pagenow_user_api
        region                  = var.region
        rds_db_name             = var.rds_db_name
        rds_username            = var.rds_username
        rds_password            = var.rds_password
        rds_port                = var.rds_port
        rds_host                = aws_db_proxy.production.endpoint
        # rds_host                = aws_db_proxy_endpoint.production-rw.endpoint
        # rds_ro_host             = aws_rds_cluster.production.reader_endpoint
        # rds_ro_host             = aws_db_proxy_endpoint.production-ro.endpoint
    }
}

resource "aws_ecs_task_definition" "app" {
    family                = "pagenow-user-api"
    container_definitions = data.template_file.app.rendered
    depends_on            = [aws_rds_cluster.production, aws_db_proxy.production]
}

resource "aws_ecs_service" "production" {
    name            = "${var.ecs_cluster_name}-service"
    cluster         = aws_ecs_cluster.production.id
    task_definition = aws_ecs_task_definition.app.arn
    iam_role        = aws_iam_role.ecs-service-role.arn
    desired_count   = var.app_count
    depends_on      = [aws_alb_listener.ecs-alb-http-listener, aws_iam_role_policy.ecs-service-role-policy, aws_db_proxy.production]

    load_balancer {
        target_group_arn = aws_alb_target_group.default-target-group.arn
        container_name   = "pagenow-user-api"
        container_port   = 8000
    }
}