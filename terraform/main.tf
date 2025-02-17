# module "pubsub" {
#   source         = "./module/pubsub"
#   project_id     = var.project_id
#   pubsub_topics  = [
#     { topic_name = var.topic_requests , subscription_name = var.sub_requests },
#     { topic_name = var.topic_helpers, subscription_name = var.sub_helpers }
#   ]
# }

# module "bigquery" {
#   source     = "./module/bigquery"
#   project_id = var.project_id
#   bq_dataset = var.bq_dataset
  
#   tables = [
#     { name = "match", schema = "schemas/match.json" },
#     { name = "no_match_voluntarios", schema = "schemas/no_match_voluntarios.json" },
#     { name = "no_matches_solicitudes", schema = "schemas/no_matches_solicitudes.json" }
#   ]
# }
# module "cloud_run_job" {
#   source             = "./module/cloud_run_job"
#   project_id         = var.project_id
#   region             = var.region
#   cloud_run_job_name = var.cloud_run_job_name
#   repository_name    = var.repository_name
#   image_name         = "data"  
#   topic_requests     = var.topic_requests
#   topic_helpers      = var.topic_helpers
#   env_vars           = {}  # O puedes pasar un mapa con variables de entorno adicionales si lo necesitas
# }
module "dataflow" {
  source             = "./module/dataflow"
  project_id         = var.project_id
  region             = var.region
  bucket             = var.bucket            # Debe existir el bucket
  repository_name    = var.repository_name
  image_name         = "dataflow"
  dataflow_job_name  = "dataflow-job"        # O usa una variable
  input_subscription = var.sub_requests      # Por ejemplo, "ayuda-sub"
  bq_dataset         = var.bq_dataset
}
resource "google_storage_bucket" "dataflow_bucket" {
  name     = var.bucket
  location = var.region

  # Opcional: Para permitir la eliminación del bucket incluso si tiene objetos.
  force_destroy = false

  uniform_bucket_level_access = true
}

module "streamlit" {
  source                = "./module/streamlit"
  project_id            = var.project_id
  region                = var.region
  service_name          = var.streamlit_service_name
  repository_name       = var.streamlit_repository_name
  image_name            = var.streamlit_image_name
  service_account_email = var.streamlit_service_account_email
}
