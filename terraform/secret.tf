# Enables the Secret Manager API for the project.
resource "google_project_service" "secretmanager" {
  service = "secretmanager.googleapis.com"

  # Prevents the API from being disabled when the resource is destroyed.
  disable_on_destroy = false
}

# Creates a Secret Manager secret to store the Sendgrid API key.
data "google_secret_manager_secret" "sendgrid_apikey" {
  secret_id = "sendgrid-apikey"

  depends_on = [ google_project_service.secretmanager ]
}

data "google_secret_manager_secret_version" "sendgrid_apikey" {
  secret = data.google_secret_manager_secret.sendgrid_apikey.id
}

# Grants the service account (this microservice) read access to the Sendgrid API key secret.
resource "google_secret_manager_secret_iam_member" "read_sendgrid_apikey" {
  secret_id = data.google_secret_manager_secret.sendgrid_apikey.id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_service_account.service.member
}
