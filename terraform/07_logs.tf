resource "aws_cloudwatch_log_group" "pagenow-user-api-log-group" {
    name              = "/ecs/pagenow-user-api"
    retention_in_days = var.log_retention_in_days
}

resource "aws_cloudwatch_log_stream" "pagenow-user-api-log-stream" {
    name           = "pagenow-user-api-log-stream"
    log_group_name = aws_cloudwatch_log_group.pagenow-user-api-log-group.name
}
