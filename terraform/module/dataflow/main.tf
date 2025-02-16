provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Construir y subir la imagen Docker
resource "null_resource" "build_push_image" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t --platform=linux/amd64 ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest .
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest
    EOT
  }
}

# 2. Subir el template spec a GCS
resource "google_storage_bucket_object" "template_spec" {
  name         = "templates/template-spec.json"
  bucket       = var.bucket
  source       = "template-spec.json"
  content_type = "application/json"

  # Aseguramos que la imagen se haya construido y subida antes de subir el template.
  depends_on = [null_resource.build_push_image]
}

# 3. Crear el job de Dataflow basado en el Flex Template
resource "google_dataflow_flex_template_job" "dataflow_job" {
  provider                = google-beta
  name                    = var.dataflow_job_name
  project                 = var.project_id
  region                  = var.region
  container_spec_gcs_path = "gs://${var.bucket}/${google_storage_bucket_object.template_spec.name}"

  parameters = {
    inputSubscription = "projects/${var.project_id}/subscriptions/${var.input_subscription}"
    bqDataset         = var.bq_dataset
  }

  on_delete = "cancel"

  depends_on = [google_storage_bucket_object.template_spec]
}
