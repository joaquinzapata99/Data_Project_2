variable "project_id" {
  description = "ID del proyecto en GCP donde se creará el Cloud Run Job"
  type        = string
}

variable "region" {
  description = "Región donde se desplegará el Cloud Run Job"
  type        = string
}

variable "cloud_run_job_name" {
  description = "Nombre del Cloud Run Job"
  type        = string
}

variable "container_image" {
  description = "Imagen del contenedor que ejecutará el Cloud Run Job"
  type        = string
}
variable "artifact_registry_dependency" {
  description = "Dependencia del módulo de artifact registry"
  type        = any
}
