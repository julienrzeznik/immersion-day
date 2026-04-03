variable "central_project_id" {
  description = "The ID of the project used as the central resource hub"
  type        = string
}

variable "region" {
  description = "The GCP region for central resources"
  type        = string
  default     = "europe-west1"
}

variable "workshop_users" {
  description = "List of email addresses for participants who need admin access to the central hub"
  type        = list(string)
  default     = []
}

variable "sandbox_project_id" {
  description = "The ID of the project used for experimentation"
  type        = string
}

variable "staging_project_id" {
  description = "The ID of the project used for staging"
  type        = string
}

variable "production_project_id" {
  description = "The ID of the project used for production"
  type        = string
}
