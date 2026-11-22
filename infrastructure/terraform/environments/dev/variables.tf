variable "name" {
  description = "Name of the demo resource."
  type        = string
  default     = "dev-demo-01"
}

variable "region" {
  description = "Logical region for the demo resource."
  type        = string
  default     = "local"
}

variable "tags" {
  description = "Tags attached to the demo resource."
  type        = map(string)
  default = {
    environment = "dev"
    managed_by  = "cloudforge"
  }
}
