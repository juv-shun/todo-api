#####################################
# CodeDeploy
#####################################
resource "aws_codedeploy_app" "codedeploy_app" {
  compute_platform = "ECS"
  name             = var.service_name
}

resource "aws_codedeploy_deployment_group" "codedeploy_deployment_group" {
  app_name               = aws_codedeploy_app.codedeploy_app.name
  deployment_config_name = "CodeDeployDefault.ECSAllAtOnce"
  deployment_group_name  = var.service_name
  service_role_arn       = aws_iam_role.code_deploy_service.arn

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout    = "STOP_DEPLOYMENT"
      wait_time_in_minutes = 20
    }

    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 30
    }
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  ecs_service {
    cluster_name = aws_ecs_cluster.cluster.name
    service_name = aws_ecs_service.service.name
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        # listener_arns = [aws_alb_listener.listener_443.arn]
        listener_arns = [aws_alb_listener.listener_80.arn]
      }
      target_group {
        name = aws_alb_target_group.target_group_blue.name
      }
      target_group {
        name = aws_alb_target_group.target_group_green.name
      }
      test_traffic_route {
        listener_arns = [aws_alb_listener.listener_8080.arn]
      }
    }
  }
}

#####################################
# IAM
#####################################
resource "aws_iam_role" "code_deploy_service" {
  name               = "${var.service_name}-codedeploy-role"
  assume_role_policy = data.aws_iam_policy_document.code_deploy_service_assume.json
}

data "aws_iam_policy_document" "code_deploy_service_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["codedeploy.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy_attachment" "code_deploy_service_ecs" {
  role       = aws_iam_role.code_deploy_service.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRoleForECS"
}

resource "aws_iam_role_policy_attachment" "code_deploy_service_role" {
  role       = aws_iam_role.code_deploy_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
}
