variable "project_id" {
  description = "The GCP project ID"
  type        = string
}
variable "region" {
  description = "The GCP region"
  type        = string
}
variable "zone" {
  description = "The GCP zone"
  type        = string
}
variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "topic_requests" {
  description = "Topico de los necesitados"
  type    = string
}

variable "topic_helpers" {
  description = "Topico de los voluntarios"
  type    = string
}
variable "sub_requests" {
  description = "Subscripcion de los necesitados"
  type    = string
}
variable "sub_helpers" {
  description = "Subscripcion de los voluntarios"
  type    = string
}
variable "bq_dataset" {
  description = "Dataset en bigquery"
  type    = string
}
variable "cloud_run_job_name" {
  type        = string
  description = "Nombre del Cloud Run Job"
}
variable "container_image" {
  type        = string
  description = "Imagen de contenedor para el Cloud Run Job"
  default     = "us-central1-docker.pkg.dev/mi-proyecto/mi-repo/mi-imagen:latest"
}
variable "image_name"{
  description = "Nombre de la imagen"
  type = string
}
variable "artifact_registry_dependency" {
  type        = any
  description = "Referencia al módulo de Artifact Registry para encadenar dependencias"
  default     = null
}
variable "bucket" {
  description = "Nombre del bucket de GCS para almacenar el template spec"
  type        = string
}
variable "streamlit_service_name" {
  description = "Nombre del servicio Cloud Run para la aplicación Streamlit"
  type        = string
}

variable "streamlit_repository_name" {
  description = "Nombre del repositorio en Artifact Registry para la imagen de Streamlit"
  type        = string
}

variable "streamlit_image_name" {
  description = "Nombre de la imagen Docker para la aplicación Streamlit"
  type        = string
}

variable "streamlit_service_account_email" {
  description = "Cuenta de servicio para el servicio de Cloud Run (opcional)"
  type        = string
  default     = ""
}