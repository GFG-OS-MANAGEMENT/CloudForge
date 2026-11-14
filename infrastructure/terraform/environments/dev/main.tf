terraform {
  required_version = ">= 1.5.0"
}

module "demo" {
  source = "../../modules/local_demo"

  name   = var.name
  region = var.region
  tags   = var.tags
}
