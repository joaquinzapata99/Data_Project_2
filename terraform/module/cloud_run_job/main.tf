resource "google_artifact_registry_repository" "repo" {
  provider      = google
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_name
  format        = "DOCKER"
}

# Autenticación con Artifact Registry
resource "null_resource" "docker_auth" {
  provisioner "local-exec" {
    command = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
  }

  depends_on = [google_artifact_registry_repository.repo]
}

# Construcción de la imagen con Docker y push a Artifact Registry
resource "null_resource" "build_push_image" {
  provisioner "local-exec" {
    command = <<EOT
      docker build --platform=linux/amd64 -t ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest ${path.module}
      docker push   ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest
    EOT
  }

  depends_on = [null_resource.docker_auth]
}

resource "google_cloud_run_v2_job" "job" {
  name     = var.cloud_run_job_name
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest"
        
        # Variables explícitas para que tu código Python las lea con os.getenv(...)
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "TOPIC_REQUESTS"
          value = var.topic_requests
        }
        env {
          name  = "TOPIC_HELPERS"
          value = var.topic_helpers
        }
        
        # Si deseas agregar variables adicionales desde un mapa (opcional)
        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = each.key
            value = each.value
          }
        }
      }
    }
  }
  deletion_protection = false
  # depends_on = [null_resource.build_push_image]
}
