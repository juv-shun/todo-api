#####################################
# ECR
#####################################
resource "aws_ecr_repository" "ecr" {
  name = var.service_name
}

resource "aws_ecr_lifecycle_policy" "ecr_lifecycle" {
  repository = aws_ecr_repository.ecr.name

  policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Delete old images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 30
        },
        "action" : {
          "type" : "expire"
        }
      }
  ] })
}

#####################################
# ECS
#####################################
resource "aws_ecs_cluster" "cluster" {
  name = var.service_name
}

resource "aws_ecs_service" "service" {
  name                              = var.service_name
  cluster                           = aws_ecs_cluster.cluster.arn
  task_definition                   = aws_ecs_task_definition.task_def.family
  desired_count                     = 1
  launch_type                       = "FARGATE"
  platform_version                  = "1.4.0"
  health_check_grace_period_seconds = 30

  deployment_controller {
    type = "CODE_DEPLOY"
  }

  load_balancer {
    container_name   = "app"
    container_port   = 80
    target_group_arn = aws_alb_target_group.target_group_blue.arn
  }

  network_configuration {
    security_groups = [aws_default_security_group.default.id]
    subnets = [
      aws_subnet.public_subnet_az1.id,
      aws_subnet.public_subnet_az2.id,
    ]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [desired_count, load_balancer, task_definition]
  }

  depends_on = [aws_alb.load_balancer]
}

resource "aws_ecs_task_definition" "task_def" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  network_mode             = "awsvpc"
  task_role_arn            = aws_iam_role.task_role.arn
  execution_role_arn       = aws_iam_role.task_exe_role.arn
  container_definitions = jsonencode([{
    name      = "app"
    image     = "${aws_ecr_repository.ecr.repository_url}:latest"
    essential = true,
    environment = [
      {
        name  = "DB_HOST"
        value = aws_rds_cluster.db_cluster.endpoint
      },
      {
        name  = "DB_USER"
        value = aws_rds_cluster.db_cluster.master_username
      },
      {
        name  = "DB_PASSWORD"
        value = aws_rds_cluster.db_cluster.master_password
      },
      {
        name  = "DB_NAME"
        value = aws_rds_cluster.db_cluster.database_name
      },
      {
        name  = "LOG_LEVEL"
        value = "error"
      },
      {
        name  = "USER_POOL_ID"
        value = aws_cognito_user_pool.pool.id
      },
      {
        name  = "APP_CLIENT_ID"
        value = aws_cognito_user_pool_client.client.id
      }
    ],
    portMappings = [
      {
        hostPort      = 80
        protocol      = "tcp"
        containerPort = 80
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/aws/ecs/${var.service_name}"
        awslogs-region        = "ap-northeast-1"
        awslogs-stream-prefix = "app"
      }
    }
  }])

  depends_on = [
    aws_cognito_user_pool.pool,
    aws_cognito_user_pool_client.client,
  ]
}

#####################################
# IAM
#####################################
resource "aws_iam_role" "task_exe_role" {
  name               = "${var.service_name}-task-exe-role"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_policy.json
}

resource "aws_iam_role" "task_role" {
  name               = "${var.service_name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_policy.json
}

resource "aws_iam_role_policy_attachment" "task_exe_role_attachment" {
  role       = aws_iam_role.task_exe_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

#####################################
# CloudWatch Logs
#####################################
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/aws/ecs/${var.service_name}"
  retention_in_days = 7
}
