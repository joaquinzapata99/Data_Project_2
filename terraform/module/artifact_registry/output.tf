output "image_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/fastapi-generator:latest"
}
output "repository" {
  value = google_artifact_registry_repository.repo
}
