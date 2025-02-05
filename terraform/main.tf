# order_events Pub/Sub topic and subscription
resource "google_pubsub_topic" "ayuda" {
  name = "ayuda"
}

resource "google_pubsub_subscription" "ayuda_sub" {
  name  = "${google_pubsub_topic.ayuda.name}-sub"
  topic = google_pubsub_topic.ayuda.name
}

# order_events Pub/Sub topic and subscription
resource "google_pubsub_topic" "voluntarios" {
  name = "voluntarios"
}

resource "google_pubsub_subscription" "voluntarios" {
  name  = "${google_pubsub_topic.voluntarios.name}-sub"
  topic = google_pubsub_topic.voluntarios.name
}

resource "google_storage_bucket" "auto-expire" {
  name          = "data-project-2"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
}