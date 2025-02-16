variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región donde se desplegará el servicio de Cloud Run (ej. europe-west1)"
  type        = string
}

variable "service_name" {
  description = "Nombre del servicio Cloud Run para la aplicación Streamlit"
  type        = string
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry (o Container Registry) donde se subirá la imagen"
  type        = string
}

variable "image_name" {
  description = "Nombre de la imagen Docker para la aplicación Streamlit"
  type        = string
}

variable "service_account_email" {
  description = "Cuenta de servicio para Cloud Run (opcional, si se deja en blanco se usará la predeterminada)"
  type        = string
  default     = ""
}
