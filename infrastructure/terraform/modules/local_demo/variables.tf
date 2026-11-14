variable "name" {
  description = "Resource name used in the generated manifest."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,39}$", var.name))
    error_message = "Name must be 3-40 characters: lowercase letters, digits or hyphens."
  }
}

variable "region" {
  description = "Logical region for the resource."
  type        = string
  default     = "local"
}

variable "tags" {
  description = "Tags attached to the resource."
  type        = map(string)
  default     = {}
}
