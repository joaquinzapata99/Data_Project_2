output "artifact_registry_repo" {
  description = "URL del repositorio en Artifact Registry"
  value       = google_artifact_registry_repository.repo.id
}
