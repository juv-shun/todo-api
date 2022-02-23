output "cognito_user_pool" {
  value = {
    user_pool_id        = aws_cognito_user_pool.pool.id
    user_pool_client_id = aws_cognito_user_pool_client.client.id
  }
}
