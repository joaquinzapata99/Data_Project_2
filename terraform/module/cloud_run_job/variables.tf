variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región donde se despliega el Cloud Run Job"
  type        = string
}

variable "cloud_run_job_name" {
  description = "Nombre del Cloud Run Job"
  type        = string
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "image_name" {
  description = "Nombre de la imagen en Artifact Registry"
  type        = string
}

variable "topic_requests" {
  description = "Nombre del tópico de requests para la aplicación Python"
  type        = string
}

variable "topic_helpers" {
  description = "Nombre del tópico de helpers para la aplicación Python"
  type        = string
}

variable "env_vars" {
  description = "Variables de entorno adicionales para el contenedor (mapa opcional)"
  type        = map(string)
  default     = {}
}
