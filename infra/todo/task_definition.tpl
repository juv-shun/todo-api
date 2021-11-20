[
  {
    "name": "app",
    "image": "${image}",
    "essential": true,
    "environment": [
      {
        "name": "DB_HOST",
        "value": "${db_host}"
      },
      {
        "name": "DB_USER",
        "value": "${db_user}"
      },
      {
        "name": "DB_PASSWORD",
        "value": "${db_password}"
      },
      {
        "name": "DB_NAME",
        "value": "${db_name}"
      },
      {
        "name": "LOG_LEVEL",
        "value": "error"
      },
      {
        "name": "USER_POOL_ID",
        "value": "${user_pool_id}"
      },
      {
        "name": "APP_CLIENT_ID",
        "value": "${user_pool_client_id}"
      }
    ],
    "portMappings": [
      {
        "hostPort": 80,
        "protocol": "tcp",
        "containerPort": 80
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${log_group}",
        "awslogs-region": "ap-northeast-1",
        "awslogs-stream-prefix": "app"
      }
    }
  }
]
