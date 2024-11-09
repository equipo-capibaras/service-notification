# Enables the IAM API for the project.
resource "google_project_service" "iam" {
  service = "iam.googleapis.com"

  # Prevents the API from being disabled when the resource is destroyed.
  disable_on_destroy = false
}

# Creates a service account for this microservice.
resource "google_service_account" "service" {
  account_id   = local.service_name
  display_name = "Service Account ${local.service_name}"

  depends_on = [ google_project_service.iam ]
}

# Retrieves the service account of the API Gateway.
# This is defined as part of the core infrastructure and is shared across all microservices.
data "google_service_account" "apigateway" {
  account_id   = "apigateway"

  depends_on = [ google_project_service.iam ]
}

# Retrieves the CircleCI service account.
# This is defined as part of the core infrastructure and is shared across all microservices.
# This service account is used by CircleCI to deploy the microservice to Cloud Run.
data "google_service_account" "circleci" {
  account_id   = "circleci"

  depends_on = [ google_project_service.iam ]
}
