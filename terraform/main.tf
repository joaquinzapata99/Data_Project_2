module "pubsub" {
  source         = "./module/pubsub"
  project_id     = var.project_id
  pubsub_topics  = [
    { topic_name = "ayuda", subscription_name = "ayuda-sub" },
    { topic_name = "voluntarios", subscription_name = "voluntarios-sub" }
  ]
}

module "bigquery" {
  source     = "./module/bigquery"
  project_id = var.project_id
  bq_dataset = "dataflow_matches"
  
  tables = [
    { name = "match", schema = "schemas/match.json" },
    { name = "no_match_voluntarios", schema = "schemas/no_match_voluntarios.json" },
    { name = "no_matches_solicitudes", schema = "schemas/no_matches_solicitudes.json" }
  ]
}

# module "artifact_registry" {
#   source           = "./module/artifact_registry"
#   project_id       = var.project_id
#   region           = var.region
#   repository_name  = var.repository_name
# }

# module "cloud_run_job" {
#   source             = "./module/cloud_run_job"
#   project_id         = var.project_id
#   region             = var.region
#   cloud_run_job_name = var.cloud_run_job_name
#   container_image    = module.artifact_registry.image_url
#   artifact_registry_dependency = module.artifact_registry
# }
