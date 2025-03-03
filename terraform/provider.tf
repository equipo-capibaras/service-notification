terraform {
  required_providers {
    google = {
      version = "~> 6.24.0"
    }
  }
}

# State is stored in a GCS bucket.
terraform {
  backend "gcs" {
    prefix = "service-notification/state"
  }
}

# Configures the Google Cloud Platform provider.
provider "google" {
  project = local.project_id
  region  = local.region
}
