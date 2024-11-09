variable "gcp_region" {
  type        = string
  default     = "us-central1"
  description = "GCP region"
}

variable "gcp_project_id" {
  type        = string
  description = "GCP project ID"
}

variable "domain" {
  type        = string
  description = "Domain name"
}
