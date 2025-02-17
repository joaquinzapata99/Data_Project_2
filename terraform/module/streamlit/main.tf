resource "null_resource" "build_push_streamlit_image" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest .
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest
    EOT
  }
}
resource "google_cloud_run_service" "streamlit_service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest"
        ports {
          container_port = 8501
        }
      }
     #service_account = (var.service_account_email != "") ? var.service_account_email : null

    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [null_resource.build_push_streamlit_image]
}

# Paso 3: Permitir acceso público al servicio (opcional)
resource "google_cloud_run_service_iam_member" "streamlit_noauth" {
  service    = google_cloud_run_service.streamlit_service.name
  location   = google_cloud_run_service.streamlit_service.location
  project    = var.project_id
  role       = "roles/run.invoker"
  member     = "allUsers"
}
