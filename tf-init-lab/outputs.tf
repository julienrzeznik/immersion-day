output "central_mcp_sa_email" {
  description = "The email address of the central MCP Service Account"
  value       = google_service_account.central_mcp_sa.email
}

output "data_bucket_name" {
  description = "The name of the GCS bucket storing the data files"
  value       = google_storage_bucket.data_bucket.name
}

output "private_products_service_url" {
  description = "The URL of the private products MCP service"
  value       = google_cloud_run_v2_service.private_products_mcp.uri
}

output "public_customers_service_url" {
  description = "The URL of the public customers MCP service"
  value       = google_cloud_run_v2_service.public_customers_mcp.uri
}

output "central_project_id" {
  description = "The ID of the central hub project"
  value       = var.central_project_id
}

output "sandbox_project_id" {
  description = "The ID of the experimentation - sandbox project"
  value       = var.sandbox_project_id
}

output "staging_project_id" {
  description = "The ID of the staging project"
  value       = var.staging_project_id
}

output "production_project_id" {
  description = "The ID of the production project"
  value       = var.production_project_id
}

output "data_bucket_path" {
  description = "The GCS path of the data bucket for RAG"
  value       = "gs://${google_storage_bucket.data_bucket.name}"
}

output "skills_bucket_path" {
  description = "The GCS path of the skills bucket"
  value       = "gs://${google_storage_bucket.skills_bucket.name}"
}

output "arize_phoenix_service_url" {
  description = "The URL of the Arize Phoenix service"
  value       = google_cloud_run_v2_service.arize_phoenix.uri
}

output "arize_phoenix_admin_password" {
  description = "The initial admin password for Arize Phoenix"
  value       = random_password.phoenix_admin_password.result
  sensitive   = true
}

output "arize_phoenix_db_password" {
  description = "The password for the Arize Phoenix database user"
  value       = random_password.phoenix_db_password.result
  sensitive   = true
}

