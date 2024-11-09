# Enables the Cloud Trace API for the project.
resource "google_project_service" "cloudtrace" {
  service = "cloudtrace.googleapis.com"

  # Prevents the API from being disabled when the resource is destroyed.
  disable_on_destroy = false
}

# Grants the service account (this microservice) the "Cloud Trace Agent" role on the project.
# This allows the service account (this microservice) to send trace data to Cloud Trace.
resource "google_project_iam_member" "cloudtrace" {
  project = local.project_id
  role    = "roles/cloudtrace.agent"
  member  = google_service_account.service.member

  depends_on = [ google_project_service.cloudtrace ]
}
