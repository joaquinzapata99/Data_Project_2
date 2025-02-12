variable "project_id" {
  description = "ID del proyecto en GCP"
  type        = string
}

variable "region" {
  description = "Región donde se creará el repositorio"
  type        = string
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}
