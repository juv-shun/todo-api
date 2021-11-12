resource "aws_rds_cluster" "db_cluster" {
  cluster_identifier              = "${var.service_name}-cluster"
  engine                          = "aurora-postgresql"
  engine_version                  = "13.4"
  master_username                 = "postgres"
  master_password                 = "password"
  database_name                   = "todo"
  vpc_security_group_ids          = [data.terraform_remote_state.network.outputs.security_group_ids["default"]]
  db_subnet_group_name            = aws_db_subnet_group.subnet_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id
  backup_retention_period         = 1
  preferred_backup_window         = "16:00-16:30"
  preferred_maintenance_window    = "mon:15:00-mon:15:30"
  copy_tags_to_snapshot           = true
  skip_final_snapshot             = true
}

resource "aws_rds_cluster_instance" "db_instance" {
  count                        = 1
  identifier                   = "todo-app-${count.index}"
  cluster_identifier           = aws_rds_cluster.db_cluster.id
  instance_class               = "db.t3.medium"
  engine                       = aws_rds_cluster.db_cluster.engine
  engine_version               = aws_rds_cluster.db_cluster.engine_version
  performance_insights_enabled = false
  auto_minor_version_upgrade   = false
}

resource "aws_db_subnet_group" "subnet_group" {
  name        = var.service_name
  description = "subnet group for todo-app"

  subnet_ids = [
    data.terraform_remote_state.network.outputs.aws_vpc_subnet_ids["private_subnet_az1"],
    data.terraform_remote_state.network.outputs.aws_vpc_subnet_ids["private_subnet_az2"],
  ]
}

resource "aws_rds_cluster_parameter_group" "cluster_parameter_group" {
  name   = var.service_name
  family = "aurora-postgresql13"

  parameter {
    name         = "timezone"
    value        = "Asia/Tokyo"
    apply_method = "pending-reboot"
  }
}
