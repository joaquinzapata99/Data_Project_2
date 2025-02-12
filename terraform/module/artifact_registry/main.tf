resource "google_artifact_registry_repository" "repo" {
  provider      = google
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_name
  format        = "DOCKER"
}

# Comando para construir y subir la imagen Docker
resource "null_resource" "docker_build_push" {
  depends_on = [google_artifact_registry_repository.repo]

    triggers = {
    always_run = timestamp() # Forzar la ejecución en cada `apply`
  }

  provisioner "local-exec" {
    command = <<EOT
      gcloud auth configure-docker ${var.region}-docker.pkg.dev
      docker build -t ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/fastapi-generator:latest -f ./app/Dockerfile ./app
      docker images | grep fastapi-generator
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/fastapi-generator:latest
      gcloud artifacts docker images list ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}

    EOT
  }
}

output "repository_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}"
}
