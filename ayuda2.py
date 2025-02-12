import apache_beam as beam
import json
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery import BigQueryDisposition

from google.cloud import bigquery

# -----------------------------
# Configuración de proyecto y BQ
# -----------------------------
project_id = "data-project-2-449815"
dataset_id = "matching_data"

table_id_matches = "matches"

# Tablas separadas para NO matches
table_id_no_matches_solicitudes = "no_matches_solicitudes"
table_id_no_matches_voluntarios = "no_matches_voluntarios"

subscription_ayuda = "ayuda-sub"
subscription_voluntarios = "voluntarios-sub"

# Tabla de correspondencia entre Nivel de Urgencia (Petición) y Nivel de Urgencias (Voluntario)
matching_criterios = {
    "Alta": ["Inmediata"],
    "Media": ["Un cafe y voy"],
    "Baja": ["Puede tardar"]
}

# Esquema para "matches": Solicitud + Voluntario
bq_schema_matches = {
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

# Esquema para solicitudes sin match (solo campos de la solicitud)
bq_schema_no_matches_solicitudes = {
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
    ]
}

# Esquema para voluntarios sin match (solo campos del voluntario)
bq_schema_no_matches_voluntarios = {
    "fields": [
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
    """Lee el JSON crudo, y retorna (Necesidad, dict_completo)."""
    message = msg.decode("utf-8")
    decodificado = json.loads(message)
    # El key para agrupar será la "Necesidad"
    return decodificado["Necesidad"], decodificado

def flatten_match_data(element):
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

def flatten_no_match_solicitud(solicitud):
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
    }

def flatten_no_match_voluntario(voluntario):
    return {
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
    Empareja solicitudes con voluntarios según:
      - Necesidad (agrupada por CoGroupByKey)
      - Nivel de Urgencia (petición) vs Nivel de Urgencias (voluntario)

    Produce TRES side outputs:
      - "matches"
      - "no_matches_solicitudes"
      - "no_matches_voluntarios"
    """
    def process(self, elemento):
        necesidad, (solicitudes, voluntarios) = elemento
        voluntarios_disponibles = list(voluntarios)  # mutable

        for solicitud in solicitudes:
            nivel_urgencia = solicitud["Nivel de Urgencia"]
            voluntarios_compatibles = [
                v for v in voluntarios_disponibles
                if v["Nivel de Urgencias"] in matching_criterios.get(nivel_urgencia, [])
            ]
            if voluntarios_compatibles:
                voluntario_asignado = voluntarios_compatibles[0]
                yield beam.pvalue.TaggedOutput("matches", {
                    "Solicitud": solicitud,
                    "Voluntario": voluntario_asignado
                })
                voluntarios_disponibles.remove(voluntario_asignado)
            else:
                yield beam.pvalue.TaggedOutput("no_matches_solicitudes", solicitud)

        # voluntarios no usados
        for voluntario_sin_usar in voluntarios_disponibles:
            yield beam.pvalue.TaggedOutput("no_matches_voluntarios", voluntario_sin_usar)

def create_dataset_if_not_exists(project_id, dataset_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = "EU" 

    try:
        client.create_dataset(dataset_ref, exists_ok=True)
        print(f"Dataset '{dataset_id}' en proyecto '{project_id}' verificado/creado.")
    except Exception as e:
        print(f"Error creando/verificando dataset: {e}")
        raise

def run():
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
            | "Decodificar ayuda" >> beam.Map(DecodificarMensaje)
            | "Ventana fija ayuda" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        datos_voluntarios = (
            p
            | "Leer datos de voluntarios" >> beam.io.ReadFromPubSub(
                subscription=f"projects/{project_id}/subscriptions/{subscription_voluntarios}",
                with_attributes=False
            )
            | "Decodificar voluntarios" >> beam.Map(DecodificarMensaje)
            | "Ventana fija voluntarios" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        grouped_data = (
            (datos_ayuda, datos_voluntarios)
            | "CoGroupByKey Necesidad" >> beam.CoGroupByKey()
        )

        # SIN especificar un main output => solo side outputs nominales
        resultado = (
            grouped_data
            | "Filtrar Matching"
            >> beam.ParDo(FiltrarMatchingPorUrgencia())
               .with_outputs("matches", "no_matches_solicitudes", "no_matches_voluntarios")
        )

        # Accedemos a cada salida por su nombre
        matches = resultado["matches"]
        no_matches_solicitudes = resultado["no_matches_solicitudes"]
        no_matches_voluntarios = resultado["no_matches_voluntarios"]

        (
            matches
            | "Aplanar matches" >> beam.Map(flatten_match_data)
            | "Escribir matches" >> beam.io.WriteToBigQuery(
                table=f"{project_id}:{dataset_id}.{table_id_matches}",
                schema=bq_schema_matches,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND
            )
        )

        (
            no_matches_solicitudes
            | "Aplanar no_matches_solicitudes" >> beam.Map(flatten_no_match_solicitud)
            | "Escribir no_matches_solicitudes" >> beam.io.WriteToBigQuery(
                table=f"{project_id}:{dataset_id}.{table_id_no_matches_solicitudes}",
                schema=bq_schema_no_matches_solicitudes,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND
            )
        )

        (
            no_matches_voluntarios
            | "Aplanar no_matches_voluntarios" >> beam.Map(flatten_no_match_voluntario)
            | "Escribir no_matches_voluntarios" >> beam.io.WriteToBigQuery(
                table=f"{project_id}:{dataset_id}.{table_id_no_matches_voluntarios}",
                schema=bq_schema_no_matches_voluntarios,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND
            )
        )

if __name__ == "__main__":
    run()