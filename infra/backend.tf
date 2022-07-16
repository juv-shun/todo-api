terraform {
  required_version = ">= 0.14.8"

  backend "s3" {
    bucket = "juv-shun.tfstate"
    key    = "todo/tfstate.tf"
    region = "ap-northeast-1"
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

data "aws_caller_identity" "aws_identity" {}

variable "service_name" {
  default = "todo-app"
}

variable "github_repository_id" {
  default = "juv-shun/todo-api"
}

variable "application-log-bucket" {
  default = "juv-shun.application-logs"
}

variable "access-log-bucket" {
  default = "juv-shun.lb-access-logs"
}

# github接続を現在terraformで行えないため、AWSコンソールで生成したのちにARNを記載する
variable "connection_star_github_arn" {}
