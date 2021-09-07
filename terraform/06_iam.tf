resource "aws_iam_role" "ecs-host-role" {
    name               = "ecs_host_role_prod"
    assume_role_policy = file("policies/ecs-role.json")
}

resource "aws_iam_role_policy" "ecs-instance-role-policy" {
    name   = "ecs_instance_role_policy"
    policy = file("policies/ecs-instance-role-policy.json")
    role   = aws_iam_role.ecs-host-role.id
}

resource "aws_iam_role" "ecs-service-role" {
    name               = "ecs_service_role_prod"
    assume_role_policy = file("policies/ecs-role.json")
}

resource "aws_iam_role_policy" "ecs-service-role-policy" {
    name   = "ecs_service_role_policy"
    policy = file("policies/ecs-service-role-policy.json")
    role   = aws_iam_role.ecs-service-role.id
}

resource "aws_iam_instance_profile" "ecs" {
    name = "ecs_instance_profile_prod"
    path = "/"
    role = aws_iam_role.ecs-host-role.name
}

resource "aws_iam_policy" "rds-proxy-role-policy" {
    name   = "rds_proxy_policy_prod"
    policy = file("policies/rds-proxy-role-policy.json")
}

resource "aws_iam_role" "rds-proxy-role" {
    name               = "rds_proxy_role_prod"
    assume_role_policy = file("policies/rds-proxy-role.json")
}

resource "aws_iam_role_policy_attachment" "rds-proxy-attach" {
    policy_arn = aws_iam_policy.rds-proxy-role-policy.arn
    role       = aws_iam_role.rds-proxy-role.name
}

