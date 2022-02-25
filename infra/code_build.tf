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
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/juv-shun/todo-api.git"
    git_clone_depth = 1
    buildspec       = "buildspec.yml"
  }
}

#####################################
# IAM
#####################################
resource "aws_iam_role" "codebuild_service_role" {
  name               = "${var.service_name}-codebuild-service-role"
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
  name   = "${var.service_name}-codebuild-policy"
  role   = aws_iam_role.codebuild_service_role.name
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Resource": "*",
            "Action": ["ecr:*"],
            "Effect": "Allow"
        },
        {
            "Resource": "*",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow"
        },
        {
            "Resource": "*",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Effect": "Allow"
        },
        {
            "Resource": "*",
            "Action": [
                "ecs:DescribeTaskDefinition"
            ],
            "Effect": "Allow"
        }
    ]
}
POLICY
}
