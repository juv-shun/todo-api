terraform {
  required_version = ">= 0.14.8"
}

provider "aws" {
  region = "ap-northeast-1"
}

data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = "../network/terraform.tfstate"
  }
}

variable "service_name" {
  default = "todo-app"
}
