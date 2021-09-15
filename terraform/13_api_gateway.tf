resource "aws_api_gateway_rest_api" "production" {
    name = "user-api-gateway"
}

resource "aws_api_gateway_resource" "production" {
    rest_api_id = aws_api_gateway_rest_api.production.id
    parent_id   = aws_api_gateway_rest_api.production.root_resource_id
    path_part   = ""
}

resource "aws_api_gateway_integration" "production" {
    rest_api_id             = aws_api_gateway_rest_api.production.id
    resource_id             = aws_api_gateway_resource.production.id
    http_method             = "ANY"
    integration_http_method = "ANY"
    type                    = "HTTP_PROXY"
    uri                     = "http://${aws_lb.production.dns_name}"
}

resource "aws_api_gateway_deployment" "production" {
    rest_api_id = aws_api_gateway_rest_api.production.id
}

resource "aws_api_gateway_stage" "production" {
    deployment_id = aws_api_gateway_deployment.production.id
    rest_api_id   = aws_api_gateway_rest_api.production.id
    stage_name    = "dev"
}
