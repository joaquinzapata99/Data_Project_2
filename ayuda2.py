import apache_beam as beam
import json
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery import BigQueryDisposition

from google.cloud import bigquery

# -----------------------------
# Configuración de proyecto y BQ
# -----------------------------
project_id = "data-project-2-449815"
dataset_id = "matching_data"  # Nombre del dataset en BigQuery
table_id = "matches"  # Nombre de la tabla en BigQuery


subscription_ayuda = "ayuda-sub"
subscription_voluntarios = "voluntarios-sub"

# Tabla de correspondencia entre Nivel de Urgencia (Petición) y Nivel de Urgencias (Voluntario)
matching_criterios = {
    "Alta": ["Inmediata"],
    "Media": ["Un café y voy"],
    "Baja": ["Puede tardar"]
}

# Definimos el esquema para la tabla de BigQuery (puedes modificarlo a tu gusto)
bq_schema = {
    "fields": [
        {"name": "Solicitud_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_Nombre", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_Edad", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Solicitud_Telefono", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_Necesidad", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_NivelUrgencia", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_Timestamp", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Solicitud_Lat", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "Solicitud_Lng", "type": "FLOAT", "mode": "NULLABLE"},

        {"name": "Voluntario_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_Nombre", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_Edad", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Voluntario_Telefono", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_Necesidad", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_NivelUrgencias", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_Timestamp", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Voluntario_Lat", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "Voluntario_Lng", "type": "FLOAT", "mode": "NULLABLE"},
    ]
}

def DecodificarMensaje(msg):
    """Decodifica un mensaje Pub/Sub y lo convierte en JSON."""
    message = msg.decode("utf-8")
    decodificado = json.loads(message)
    # Agrupamos por "Necesidad"
    return decodificado["Necesidad"], decodificado

def flatten_match_data(element):
    """
    Recibe un diccionario:
      {
        'Solicitud': {...},
        'Voluntario': {...}
      }
    y lo aplana según el bq_schema definido.
    """
    solicitud = element["Solicitud"]
    voluntario = element["Voluntario"]

    return {
        "Solicitud_ID": solicitud["ID"],
        "Solicitud_Nombre": solicitud["Nombre"],
        "Solicitud_Edad": solicitud["Edad"],
        "Solicitud_Telefono": solicitud["Telefono"],
        "Solicitud_Necesidad": solicitud["Necesidad"],
        "Solicitud_NivelUrgencia": solicitud["Nivel de Urgencia"],
        "Solicitud_Timestamp": solicitud["Timestamp"],
        "Solicitud_Lat": solicitud["Ubicacion"]["latitud"],
        "Solicitud_Lng": solicitud["Ubicacion"]["longitud"],

        "Voluntario_ID": voluntario["ID"],
        "Voluntario_Nombre": voluntario["Nombre"],
        "Voluntario_Edad": voluntario["Edad"],
        "Voluntario_Telefono": voluntario["Telefono"],
        "Voluntario_Necesidad": voluntario["Necesidad"],
        "Voluntario_NivelUrgencias": voluntario["Nivel de Urgencias"],
        "Voluntario_Timestamp": voluntario["Timestamp"],
        "Voluntario_Lat": voluntario["Ubicacion"]["latitud"],
        "Voluntario_Lng": voluntario["Ubicacion"]["longitud"],
    }

class FiltrarMatchingPorUrgencia(beam.DoFn):
    """
    Empareja peticiones de ayuda con voluntarios según:
    - Necesidad (ya agrupada por CoGroupByKey)
    - Nivel de Urgencia (petición) vs Nivel de Urgencias (voluntario)
    """
    def process(self, elemento):
        # elemento = (necesidad, (solicitudes, voluntarios))
        necesidad, (solicitudes, voluntarios) = elemento

        for solicitud in solicitudes:
            nivel_urgencia = solicitud["Nivel de Urgencia"]

            # Filtrar voluntarios compatibles según la tabla de matching
            voluntarios_compatibles = [
                v for v in voluntarios 
                if v["Nivel de Urgencias"] in matching_criterios[nivel_urgencia]
            ]

            if voluntarios_compatibles:
                voluntario_asignado = voluntarios_compatibles[0]  # Tomamos el primer voluntario compatible
                yield beam.pvalue.TaggedOutput("matches", {
                    "Solicitud": solicitud,
                    "Voluntario": voluntario_asignado
                })
            else:
                yield beam.pvalue.TaggedOutput("no_matches", solicitud)  # Peticiones sin match

def create_dataset_if_not_exists(project_id, dataset_id):
    """
    Crea el dataset si no existe. Si existe, no hace nada.
    """
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    # Opcional: ubicación del dataset (puedes usar EU, US, o europe-west1, etc.)
    dataset_ref.location = "EU"  

    try:
        client.create_dataset(dataset_ref, exists_ok=True)
        print(f"Dataset '{dataset_id}' en proyecto '{project_id}' verificado/creado.")
    except Exception as e:
        print(f"Error creando/verificando dataset: {e}")
        raise

def run():
    # Antes de lanzar el pipeline, nos aseguramos de que el dataset exista
    create_dataset_if_not_exists(project_id, dataset_id)

    pipeline_options = PipelineOptions(
        streaming=True,
        save_main_session=True,
        runner='DataflowRunner',
        project=project_id,
        job_name='pubsub-matching-job',
        region='europe-west1',
        temp_location='gs://data-project-2/temp',
        staging_location='gs://data-project-2/staging'
    )

    with beam.Pipeline(options=pipeline_options) as p:
        datos_ayuda = (
            p
            | "Leer datos de ayuda" >> beam.io.ReadFromPubSub(
                subscription=f"projects/{project_id}/subscriptions/{subscription_ayuda}",
                with_attributes=False
            )
            | "Decodificar mensajes de ayuda" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de ayuda" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        datos_voluntarios = (
            p
            | "Leer datos de voluntarios" >> beam.io.ReadFromPubSub(
                subscription=f"projects/{project_id}/subscriptions/{subscription_voluntarios}",
                with_attributes=False
            )
            | "Decodificar mensajes de voluntarios" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de voluntarios" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        grouped_data = (
            (datos_ayuda, datos_voluntarios)
            | "Juntar por necesidad" >> beam.CoGroupByKey()
        )

        # Aplicar el DoFn para hacer el matching
        emparejamientos = (
            grouped_data
            | "Filtrar Matching" 
            >> beam.ParDo(FiltrarMatchingPorUrgencia()).with_outputs("matches", "no_matches")
        )

        matches = emparejamientos.matches
        no_matches = emparejamientos.no_matches

        # 1) Transformar matches al formato esperado e insertar en BigQuery
        (
            matches
            | "Aplanar matches" >> beam.Map(flatten_match_data)
            | "Escribir en BigQuery" >> beam.io.WriteToBigQuery(
                # dataset.tabla (por ejemplo data-project-2-449815:mi_dataset.mi_tabla)
                table=f"{project_id}:{dataset_id}.{table_id}",
                schema=bq_schema,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND
            )
        )

        # 2) Imprimir los no_matches
        no_matches | "Print No Matches" >> beam.Map(print)

# Ejecutar el proceso
if __name__ == "__main__":
    run()
