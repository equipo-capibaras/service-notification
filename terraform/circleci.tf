# Grants the CircleCI service account the ability to act as the service account of this microservice.
# This is required for CircleCI to be able to deploy the service to Cloud Run.
resource "google_project_iam_member" "circleci_cloud_run_service_account" {
  project = local.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = data.google_service_account.circleci.member

  condition {
    title       = "Service Account ${local.service_name}"
    expression  = "resource.name == \"projects/-/serviceAccounts/${google_service_account.service.unique_id}\""
  }
}
