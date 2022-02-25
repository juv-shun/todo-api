resource "aws_cognito_user_pool" "pool" {
  name                       = var.service_name
  auto_verified_attributes   = ["email"]
  sms_authentication_message = " 認証コードは {####} です。"

  username_configuration {
    case_sensitive = false
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    name                     = "email"
    required                 = true

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = false
    require_uppercase                = true
    temporary_password_validity_days = 7
  }
}

resource "aws_cognito_user_pool_client" "client" {
  user_pool_id           = aws_cognito_user_pool.pool.id
  name                   = "${var.service_name}-clinet"
  id_token_validity      = 60
  refresh_token_validity = 30
  access_token_validity  = 60

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]

  read_attributes  = ["email", "email_verified", "name"]
  write_attributes = ["email", "name"]
}
