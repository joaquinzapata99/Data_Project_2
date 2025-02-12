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
variable "subnetwork" {
  description = "The subnetwork for the instances"
  type        = string
}

variable "service_account_email" {
  description = "Email of the service account to attach to the VMs"
  type        = string
}
variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "cloud_run_job_name" {
  description = "Nombre del Cloud Run Job"
  type        = string
}
