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

variable "repository_name_dataflow" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "table_match" {
  description = "Tabla Big Query matcheo"
  type = string
  
}
variable "image_name_dataflow" {
  type        = string
  description = "Nombre de la imagen para Dataflow"
}
variable "table_no_vol" {
  description = "Tabla Big Query no match voluntarios"
  type = string
}
variable "table_no_sol" {
  description = "Tabla Big Query no match solicitudes"
  type = string 
}
variable "sub_requests" {
  description = "Nombre del tópico de requests para la aplicación Python"
  type        = string
}

variable "sub_helpers" {
  description = "Nombre del tópico de helpers para la aplicación Python"
  type        = string
}
