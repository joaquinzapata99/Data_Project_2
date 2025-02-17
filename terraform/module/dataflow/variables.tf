variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región de GCP (por ejemplo, europe-west1)"
  type        = string
}

variable "bucket" {
  description = "Nombre del bucket de GCS para almacenar el template spec"
  type        = string
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "image_name" {
  description = "Nombre de la imagen Docker"
  type        = string
}

variable "dataflow_job_name" {
  description = "Nombre del job de Dataflow"
  type        = string
}

variable "input_subscription" {
  description = "Nombre de la suscripción de Pub/Sub para el input del pipeline"
  type        = string
}

variable "bq_dataset" {
  description = "Dataset de BigQuery donde se volcará la salida"
  type        = string
}
