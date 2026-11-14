# A safe, offline demo module. It writes a manifest describing the requested
# resource instead of creating billable cloud infrastructure. This keeps the
# provisioning pipeline testable without cloud credentials.
locals {
  manifest = {
    managed_by = "CloudForge"
    name       = var.name
    region     = var.region
    tags       = var.tags
    created_at = timestamp()
  }
}

resource "local_file" "manifest" {
  filename        = "${path.root}/generated/${var.name}.json"
  content         = jsonencode(local.manifest)
  file_permission = "0644"
}
