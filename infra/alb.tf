#####################################
# ALB
#####################################
resource "aws_alb" "load_balancer" {
  name = var.service_name
  security_groups = [
    aws_default_security_group.default.id,
    aws_security_group.http_sg.id
  ]
  subnets = [
    aws_subnet.public_subnet_az1.id,
    aws_subnet.public_subnet_az2.id,
  ]

  access_logs {
    bucket  = aws_s3_bucket.access_logs.id
    enabled = true
  }

  depends_on = [aws_s3_bucket.access_logs]
}

#####################################
# Access log Bucket
#####################################
resource "aws_s3_bucket" "access_logs" {
  bucket        = "${var.service_name}-access-logs"
  force_destroy = true
}

resource "aws_s3_bucket_policy" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::582318560864:root"
        },
        "Action" : "s3:PutObject",
        "Resource" : "arn:aws:s3:::${aws_s3_bucket.access_logs.id}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket.access_logs, aws_s3_bucket_public_access_block.access_logs]
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket                  = aws_s3_bucket.access_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#####################################
# Listener
#####################################
# resource "aws_alb_listener" "listener_443" {
#   load_balancer_arn = aws_alb.load_balancer.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08"
#   certificate_arn   = var.certificate_arn

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_alb_target_group.target_group.arn
#   }

#   lifecycle {
#     ignore_changes = [default_action]
#   }
# }

resource "aws_alb_listener" "listener_80" {
  load_balancer_arn = aws_alb.load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.target_group_blue.arn

    # type = "redirect"
    # redirect {
    #   port        = "443"
    #   protocol    = "HTTPS"
    #   status_code = "HTTP_301"
    # }
  }

  lifecycle {
    ignore_changes = [default_action]
  }
}

resource "aws_alb_listener" "listener_8080" {
  load_balancer_arn = aws_alb.load_balancer.arn
  port              = 8080
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.target_group_green.arn
    type             = "forward"
  }

  lifecycle {
    ignore_changes = [default_action]
  }
}

#####################################
# Target Group
#####################################
resource "aws_alb_target_group" "target_group_blue" {
  name                 = "${var.service_name}-target-blue"
  port                 = 80
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = aws_vpc.main.id
  deregistration_delay = 90

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 4
    interval            = 30
    matcher             = 200
    path                = "/heartbeat"
    protocol            = "HTTP"
    timeout             = 5
  }
}

resource "aws_alb_target_group" "target_group_green" {
  name                 = "${var.service_name}-target-green"
  port                 = 80
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = aws_vpc.main.id
  deregistration_delay = 90

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 4
    interval            = 30
    matcher             = 200
    path                = "/heartbeat"
    protocol            = "HTTP"
    timeout             = 5
  }
}

#####################################
# Security Group
#####################################
resource "aws_security_group" "http_sg" {
  name        = "${var.service_name}-http-sg"
  description = "Allow HTTP inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "[${var.service_name}] http"
  }
}
