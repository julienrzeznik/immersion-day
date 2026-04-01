provider "google" {
  project = var.central_project_id
  region  = var.region
}

# Enable necessary APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com", 
    "storage.googleapis.com",
    "iam.googleapis.com",
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "secretmanager.googleapis.com",
    "bigquery.googleapis.com",
    "apihub.googleapis.com",
    "cloudkms.googleapis.com",
    "apigee.googleapis.com",
    "cloudapiregistry.googleapis.com"
  ])

  project = var.central_project_id
  service = each.key

  disable_on_destroy         = false
  disable_dependent_services = false
}

# Create a single service account for the MCP servers
resource "google_service_account" "central_mcp_sa" {
  account_id   = "central-mcp-sa"
  display_name = "Central MCP Service Account"
  project      = var.central_project_id

  depends_on = [google_project_service.required_apis]
}

# Create GCS Bucket for data storage
resource "google_storage_bucket" "data_bucket" {
  name          = "${var.central_project_id}-data-bucket"
  location      = var.region
  project       = var.central_project_id
  force_destroy = true

  uniform_bucket_level_access = true

  depends_on = [google_project_service.required_apis]
}

# Upload data.pdf to the GCS bucket
resource "google_storage_bucket_object" "data_pdf" {
  name   = "data.pdf"
  source = "${path.module}/files/data.pdf"
  bucket = google_storage_bucket.data_bucket.name
}

# Create GCS Bucket for skills
resource "google_storage_bucket" "skills_bucket" {
  name          = "${var.central_project_id}-skills"
  location      = var.region
  project       = var.central_project_id
  force_destroy = true

  uniform_bucket_level_access = true

  depends_on = [google_project_service.required_apis]
}

# Create BigQuery dataset for the workshop
resource "google_bigquery_dataset" "workshop_dataset" {
  dataset_id                  = "workshop_dataset"
  friendly_name               = "Workshop Dataset"
  description                 = "Dataset for workshop sample data"
  location                    = "EU"
  project                     = var.central_project_id
  delete_contents_on_destroy = true

  depends_on = [google_project_service.required_apis]
}


# Create a sample table in the dataset (View with hardcoded data)
resource "google_bigquery_table" "sample_table" {
  dataset_id = google_bigquery_dataset.workshop_dataset.dataset_id
  table_id   = "sample_table"
  project    = var.central_project_id

  view {
    query = <<-EOT
      SELECT 1 AS id, 'Hello from Terraform' AS message
      UNION ALL
      SELECT 2, 'Welcome to the AI Workshop'
      UNION ALL
      SELECT 3, 'This is a BigQuery View'
    EOT
    use_legacy_sql = false
  }

  deletion_protection = false

  depends_on = [google_bigquery_dataset.workshop_dataset]
}

# --- API Hub Configuration ---

# Register the project as an API Hub host
resource "google_apihub_host_project_registration" "apihub_host" {
  project                      = var.central_project_id
  location                     = var.region
  host_project_registration_id = var.central_project_id
  gcp_project                 = "projects/${var.central_project_id}"
  depends_on                  = [google_project_service.required_apis]
}

# Create Service Identity for API Hub
resource "google_project_service_identity" "apihub_sa" {
  provider = google-beta
  project  = var.central_project_id
  service  = "apihub.googleapis.com"
}

# Assign required roles to the Service Identity
resource "google_project_iam_member" "apihub_sa_roles" {
  for_each = toset([
    "roles/apihub.admin",
    "roles/apihub.runtimeProjectServiceAgent"
  ])
  project = var.central_project_id
  role    = each.key
  member  = "serviceAccount:${google_project_service_identity.apihub_sa.email}"
}

# Create the API Hub Instance
resource "google_apihub_api_hub_instance" "apihub_instance" {
  project  = var.central_project_id
  location = var.region
  config {
    disable_search = true
  }
  depends_on = [
    google_apihub_host_project_registration.apihub_host,
    google_project_iam_member.apihub_sa_roles
  ]
}

# Cloud Run Service 1: private-products-mcp
resource "google_cloud_run_v2_service" "private_products_mcp" {
  name     = "products-mcp"
  location = var.region
  project  = var.central_project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  # We use a dummy image initially so terraform can create the service
  # The actual image will be deployed via "make deploy" in the application folder
  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
    }
    service_account = google_service_account.central_mcp_sa.email
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
      labels,
      annotations
    ]
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run Service 2: public_customers-mcp
resource "google_cloud_run_v2_service" "public_customers_mcp" {
  name     = "customers-mcp"
  location = var.region
  project  = var.central_project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
    }
    service_account = google_service_account.central_mcp_sa.email
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
      labels,
      annotations
    ]
  }

  depends_on = [google_project_service.required_apis]
}

data "google_project" "project" {
  project_id = var.central_project_id
}

locals {
  compute_sa_roles = [
    "roles/storage.admin",
    "roles/artifactregistry.admin",
    "roles/logging.logWriter",
    "roles/cloudbuild.builds.builder"
  ]
}

# Grant the default Compute Engine service account access to build and push images
resource "google_project_iam_member" "compute_sa_roles" {
  for_each = toset(local.compute_sa_roles)

  project = var.central_project_id
  role    = each.key
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"

  depends_on = [google_project_service.required_apis]
}

locals {
  participant_roles = [
    "roles/run.admin",
    "roles/discoveryengine.admin",
    "roles/secretmanager.admin",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/storage.admin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/bigquery.user",
    "roles/bigquery.dataViewer",
    "roles/cloudapiregistry.admin",
    "roles/apihub.viewer",
    "roles/apihub.editor"
  ]

  # Map every user to every role
  participant_iam_bindings = flatten([
    for user_email in var.workshop_users : [
      for role in local.participant_roles : {
        user_email = user_email
        role       = role
      }
    ]
  ])
}

# Grant admin permissions to all participants in the workshop_users list
resource "google_project_iam_member" "participant_admin_roles" {
  for_each = {
    for binding in local.participant_iam_bindings : "${binding.user_email}_${binding.role}" => binding
  }

  project = var.central_project_id
  role    = each.value.role
  member  = "user:${each.value.user_email}"

  depends_on = [google_project_service.required_apis]
}

# Activate AI Companion API in the experimentation project
resource "google_project_service" "experimentation_ai_companion" {
  project = var.sandbox_project_id
  service = "cloudaicompanion.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Activate AI platform API in the experimentation project
resource "google_project_service" "experimentation_ai_platform" {
  project = var.sandbox_project_id
  service = "aiplatform.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Activate Cloud Resource Manager API in the experimentation project
resource "google_project_service" "experimentation_cloudresourcemanager" {
  project = var.sandbox_project_id
  service = "cloudresourcemanager.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

locals {
  experimentation_participant_roles = [
    "roles/aiplatform.user",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/serviceusage.serviceUsageAdmin",
    "roles/run.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/storage.admin",
    "roles/secretmanager.admin",
    "roles/cloudbuild.builds.editor",
    "roles/discoveryengine.admin",
    "roles/editor",
    "roles/logging.admin",
    "roles/bigquery.admin",
    "roles/iam.serviceAccountUser"
  ]

  agent_projects = [
    var.sandbox_project_id,
    var.staging_project_id,
    var.production_project_id
  ]

  participant_project_iam_bindings = flatten([
    for project_id in local.agent_projects : [
      for user_email in var.workshop_users : [
        for role in local.experimentation_participant_roles : {
          project_id = project_id
          user_email = user_email
          role       = role
        }
      ]
    ]
  ])
}

# Grant required roles across dev, staging, and prod projects to all participants
resource "google_project_iam_member" "participant_project_roles" {
  for_each = {
    for binding in local.participant_project_iam_bindings : "${binding.project_id}_${binding.user_email}_${binding.role}" => binding
  }

  project = each.value.project_id
  role    = each.value.role
  member  = "user:${each.value.user_email}"

  depends_on = [google_project_service.experimentation_ai_platform]
}

# ------------------------------------------------------------------------------
# Secrets Creation
# ------------------------------------------------------------------------------

resource "google_secret_manager_secret" "github_pat" {
  project   = var.central_project_id
  secret_id = "github_pat"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "github_pat_version" {
  secret      = google_secret_manager_secret.github_pat.id
  secret_data = "TO_BE_DEFINED"
}

resource "google_secret_manager_secret" "github_oauth_app" {
  project   = var.central_project_id
  secret_id = "github_oauth_app"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "github_oauth_app_version" {
  secret      = google_secret_manager_secret.github_oauth_app.id
  secret_data = "TO_BE_DEFINED"
}
