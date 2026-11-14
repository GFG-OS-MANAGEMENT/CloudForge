output "manifest_path" {
  description = "Path to the generated resource manifest."
  value       = local_file.manifest.filename
}

output "resource_name" {
  description = "Name of the provisioned resource."
  value       = var.name
}
