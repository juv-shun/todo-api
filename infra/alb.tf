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
    bucket  = var.access-log-bucket
    prefix  = var.service_name
    enabled = true
  }
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
