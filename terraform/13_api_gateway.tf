resource "aws_api_gateway_rest_api" "production" {
    name = "user-api-gateway"
}

# resource "aws_api_gateway_resource" "production" {
#     rest_api_id = aws_api_gateway_rest_api.production.id
#     parent_id   = aws_api_gateway_rest_api.production.root_resource_id
#     path_part   = "{proxy+}"
# }

# resource "aws_api_gateway_authorizer" "production" {
#     name          = "CognitoUserPoolAuthorizer"
#     type          = "COGNITO_USER_POOLS"
#     rest_api_id   = aws_api_gateway_rest_api.production.id
#     provider_arns = data.aws_cognito_user_pools.this.arns
# }

# resource "aws_api_gateway_method" "production" {
#     rest_api_id   = aws_api_gateway_rest_api.production.id
#     resource_id   = aws_api_gateway_resource.production.id
#     http_method   = "ANY"
#     authorization = "NONE"
# #   authorization = "COGNITO_USER_POOLS"
# #   authorizer_id = aws_api_gateway_authorizer.this.id

#     request_parameters = {
#         "method.request.path.proxy" = true
#     }
# }

# resource "aws_api_gateway_integration" "production" {
#     rest_api_id             = aws_api_gateway_rest_api.production.id
#     resource_id             = aws_api_gateway_resource.production.id
#     http_method             = aws_api_gateway_method.production.http_method
#     integration_http_method = "ANY"
#     type                    = "HTTP_PROXY"
#     uri                     = "http://${aws_lb.production.dns_name}/{proxy}"

#     request_parameters = {
#         "integration.request.path.proxy" = true
#     }
# }

resource "aws_api_gateway_deployment" "production" {
    rest_api_id = aws_api_gateway_rest_api.production.id
}

resource "aws_api_gateway_stage" "production" {
    deployment_id = aws_api_gateway_deployment.production.id
    rest_api_id   = aws_api_gateway_rest_api.production.id
    stage_name    = "dev"
}
