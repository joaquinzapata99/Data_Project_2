provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Construir y subir la imagen Docker (incluye el script que inicia Dataflow)
resource "null_resource" "build_push_image" {
  provisioner "local-exec" {
    command = <<EOT
      docker build --platform=linux/amd64 -t ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest ${path.module}
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest
    EOT
  }
}

# 2. (Opcional) Ejecutar el contenedor para iniciar el Dataflow
# Puedes ejecutar el contenedor localmente o usar otro recurso/servicio que lo haga.
# Por ejemplo, si deseas ejecutar el contenedor localmente desde Terraform:
resource "null_resource" "run_container" {
  depends_on = [null_resource.build_push_image]
  provisioner "local-exec" {
    command = <<EOT
      docker run ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest
    EOT
  }
}
