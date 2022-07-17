resource "aws_codebuild_project" "codebuild" {
  name          = var.service_name
  description   = "image build for ${var.service_name}"
  service_role  = aws_iam_role.codebuild_service_role.arn
  build_timeout = 60

  artifacts {
    type = "NO_ARTIFACTS"
  }

  cache {
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
    type  = "LOCAL"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true

    environment_variable {
      name  = "ECS_TASK_DEFINITION_ARN"
      value = aws_ecs_task_definition.task_def.arn
    }

    environment_variable {
      name  = "REPOSTORY_NAME"
      value = aws_ecr_repository.ecr.name
    }
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/${var.github_repository_id}.git"
    git_clone_depth = 1
    buildspec       = "buildspec.yml"
    git_submodules_config {
      fetch_submodules = false
    }
  }
}

#####################################
# IAM
#####################################
resource "aws_iam_role" "codebuild_service_role" {
  name               = "${var.service_name}-codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild_service_role_assume_policy.json
}

data "aws_iam_policy_document" "codebuild_service_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "codebuild_service_role" {
  name = "${var.service_name}-codebuild-policy"
  role = aws_iam_role.codebuild_service_role.name
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Resource" : "*",
          "Action" : "ecr:GetAuthorizationToken",
          "Effect" : "Allow"
        },
        {
          "Resource" : aws_ecr_repository.ecr.arn,
          "Action" : ["ecr:*"],
          "Effect" : "Allow"
        },
        {
          "Resource" : aws_cloudwatch_log_group.code_build_log_group.arn,
          "Action" : [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Effect" : "Allow"
        },
        {
          "Resource" : ["${aws_s3_bucket.pipeline_artifact.arn}*"]
          "Action" : [
            "s3:PutObject",
            "s3:GetObject",
            "s3:GetObjectVersion"
          ],
          "Effect" : "Allow"
        },
        {
          "Resource" : "*",
          "Action" : [
            "ecs:DescribeTaskDefinition"
          ],
          "Effect" : "Allow"
        }
      ]
  })
}

#####################################
# CloudWatch Logs
#####################################
resource "aws_cloudwatch_log_group" "code_build_log_group" {
  name              = "/aws/codebuild/${var.service_name}"
  retention_in_days = 7
}
