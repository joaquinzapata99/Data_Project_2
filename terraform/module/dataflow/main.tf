resource "google_storage_bucket" "dataflow_bucket" {
    name     = var.bucket
    location = var.region
    project  = var.project_id 
    storage_class = "STANDARD"
  
}

resource "google_storage_bucket_object" "tmp_folder" {
    name   = "tmp/"
    bucket = var.bucket
    content = ""
}

resource "google_storage_bucket_object" "stg_folder" {
    name   = "stg/"
    bucket = var.bucket
    content = ""
}

resource "google_artifact_registry_repository" "repo" {
    project       = var.project_id
    location      = var.region
    repository_id = var.repository_name_dataflow
    format        = "DOCKER"
  
}

resource "null_resource" "build_push_image" {
  depends_on = [ google_artifact_registry_repository.repo ]

  provisioner "local-exec" {
    command = <<EOT
      docker build --platform=linux/amd64 -t ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name_dataflow}/${var.image_name_dataflow}:latest ${path.module}
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name_dataflow}/${var.image_name_dataflow}:latest
    EOT
  }
}

resource "google_cloud_run_v2_job" "dataflow" {
  name = "dataflow"
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {

      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name_dataflow}/${var.image_name_dataflow}:latest"
      env {
        name = "project_id"
        value = var.project_id
      }
      env {
        name  = "table_id_matches"
        value = var.table_match
      }
      env {
        name  = "bq_dataset"
        value = var.bq_dataset
      }
      env {
        name  = "table_id_no_matches_solicitudes"
        value = var.table_no_sol
      }
      env {
        name  = "table_id_no_matches_voluntarios"
        value = var.table_no_vol
      }
      env {
        name  = "sub_requests"
        value = var.sub_requests
      }
      env {
        name  = "sub_helpers"
        value = var.sub_helpers
      }
              resources {
          limits = {
            memory = "8Gi"
            cpu    = "2"
          }
        }
      }
      max_retries = 3
    }
  }

  depends_on = [
    google_artifact_registry_repository.repo,
    null_resource.build_and_push_docker
  ]
}
  
