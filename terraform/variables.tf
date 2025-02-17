variable "project_id" {
  description = "ID del proyecto de GCP."
  type        = string
}

variable "zone" {
  description = "Zona del proyecto"
  type        = string
}
variable "topic_requests" {
  description = "Nombre del tópico de requests."
  type        = string
}

variable "sub_requests" {
  description = "Nombre de la suscripción de requests."
  type        = string
}

variable "topic_helpers" {
  description = "Nombre del tópico de helpers."
  type        = string
}

variable "sub_helpers" {
  description = "Nombre de la suscripción de helpers."
  type        = string
}

variable "bq_dataset" {
  description = "Nombre del dataset de BigQuery."
  type        = string
}

variable "region" {
  description = "Región de GCP donde se desplegarán los recursos."
  type        = string
}

variable "cloud_run_job_generator" {
  description = "Nombre del job de Cloud Run para el generador."
  type        = string
}

variable "repository_name_generator" {
  description = "Nombre del repositorio para el generador en Cloud Run."
  type        = string
}

variable "image_name_generator" {
  description = "Nombre de la imagen para el generador en Cloud Run."
  type        = string
}

variable "bucket" {
  description = "Nombre del bucket para Dataflow."
  type        = string
}

variable "repository_name_dataflow" {
  description = "Nombre del repositorio para Dataflow."
  type        = string
}

variable "image_name_dataflow" {
  description = "Nombre de la imagen para Dataflow."
  type        = string
}

variable "cloud_run_job_dataflow" {
  description = "Nombre del job de Dataflow (en este caso, se usa la variable cloud_run_job_dataflow)."
  type        = string
}

variable "match" {
  description = "Nombre de la tabla de BigQuery para los datos de match."
  type        = string
}

variable "no_matches_solicitudes" {
  description = "Nombre de la tabla de BigQuery para los datos de no match solicitudes."
  type        = string
}

variable "no_matches_voluntarios" {
  description = "Nombre de la tabla de BigQuery para los datos de no match solicitudes."
  type        = string
}
