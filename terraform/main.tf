module "pubsub" {
  source         = "./module/pubsub"
  project_id     = var.project_id
  pubsub_topics  = [
    { topic_name = var.topic_requests , subscription_name = var.sub_requests },
    { topic_name = var.topic_helpers, subscription_name = var.sub_helpers }
  ]
}

module "bigquery" {
  source     = "./module/bigquery"
  project_id = var.project_id
  bq_dataset = var.bq_dataset
  
  tables = [
    { name = "match", schema = "schemas/match.json" },
    { name = "no_match_voluntarios", schema = "schemas/no_match_voluntarios.json" },
    { name = "no_matches_solicitudes", schema = "schemas/no_matches_solicitudes.json" }
  ]
}

module "cloud_run_generator" {
  source             = "./module/cloud_run_generator"
  project_id         = var.project_id
  region             = var.region
  cloud_run_job_name = var.cloud_run_job_generator
  repository_name    = var.repository_name_generator
  image_name         = var.image_name_generator  
  topic_requests     = var.topic_requests
  topic_helpers      = var.topic_helpers
}

module "dataflow" {
  source                   = "./module/dataflow"
  project_id               = var.project_id
  region                   = var.region
  bucket                   = var.bucket
  repository_name_dataflow = var.repository_name_dataflow
  image_name_dataflow      = var.image_name_dataflow
  dataflow_job_name        = var.cloud_run_job_dataflow
  input_subscription       = var.sub_requests
  bq_dataset               = var.bq_dataset
  table_match              = var.match
  table_no_sol             = var.no_matches_solicitudes
  table_no_vol             = var.no_matches_voluntarios
  sub_requests             = var.sub_requests
  sub_helpers              = var.sub_helpers
}

# module "streamlit" {
#   source                = "./module/streamlit"
#   project_id            = var.project_id
#   region                = var.region
#   service_name          = var.streamlit_service_name
#   repository_name       = var.streamlit_repository_name
#   image_name            = var.streamlit_image_name
#   service_account_email = var.streamlit_service_account_email
# }
