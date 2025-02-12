# resource "google_cloud_run_v2_job" "cloud_run_job" {
#   name     = var.cloud_run_job_name
#   location = var.region
#   project  = var.project_id

# deletion_protection = false

#   template {
#     template {
#       containers {
#         image = var.container_image

#         resources {
#           limits = {
#             cpu    = "1"
#             memory = "512Mi"
#           }
#         }
#       }
#     }
#   }

#     depends_on = [var.artifact_registry_dependency]
# }
