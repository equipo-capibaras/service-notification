data "google_pubsub_topic" "incident_update" {
  name = "incident-update"
}

resource "google_pubsub_subscription" "default" {
  name  = "incident-update-${local.service_name}"
  topic = data.google_pubsub_topic.incident_update.id

  ack_deadline_seconds = 20

  push_config {
    push_endpoint = "https://${local.service_name}-${data.google_project.default.number}.${local.region}.run.app/api/v1/incident-update/${local.service_name}"

    attributes = {
      x-goog-version = "v1"
    }

    no_wrapper {
        write_metadata = true
    }

    oidc_token {
      service_account_email = data.google_service_account.pubsub.email
      audience = "https://${local.service_name}-${data.google_project.default.number}.${local.region}.run.app"
    }
  }

  retry_policy {
    minimum_backoff = "1s"
    maximum_backoff = "600s"
  }
}
