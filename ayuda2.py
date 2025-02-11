import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from datetime import datetime
import logging
import json

project_id = "data-project-2-449815"
subscription_ayuda = "ayuda-sub"
subscription_voluntarios = "voluntarios-sub"

dataset_id = "dataflow_matches"
matches_table = "matches"
no_matches_table = "no_matches"

MATCHES_TAG = "matches"
NO_MATCH_TAG = "no_matches"

urgencias_map = {
    "Alta": "Inmediata",
    "Media": "Un café y voy",
    "Baja": "Puede tardar"
}

def DecodificarMensaje(msg):
    try:
        message = msg.decode("utf-8")
        decodificado = json.loads(message)
        return decodificado["Necesidad"], decodificado
    except Exception as e:
        logging.error(f"Error decodificando mensaje: {msg} - {e}")
        return None

def FiltrarYEmparejar(elemento):
    try:
        if not isinstance(elemento, tuple) or len(elemento) != 2:
            return []
        
        necesidad, datos = elemento
        peticiones = datos.get(subscription_ayuda, [])
        voluntarios = datos.get(subscription_voluntarios, [])

        logging.info(f"Procesando necesidad: {necesidad}, Peticiones: {len(peticiones)}, Voluntarios: {len(voluntarios)}")

        for peticion in peticiones:
            matched = False
            for voluntario in voluntarios:
                if (
                    peticion.get("Nivel de Urgencia") == urgencias_map.get(voluntario.get("Nivel de Urgencias"))
                    and peticion.get("ID", "").startswith("A")
                    and voluntario.get("ID", "").startswith("V")
                ):
                    yield beam.pvalue.TaggedOutput(MATCHES_TAG, {"peticion": peticion, "voluntario": voluntario})
                    matched = True
                    break
            if not matched:
                yield beam.pvalue.TaggedOutput(NO_MATCH_TAG, {"peticion": peticion})
    except Exception as e:
        logging.error(f"Error en FiltrarYEmparejar con elemento {elemento}: {e}")

def run():
    job_name = f"pubsub-matching-job-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    pipeline_options = PipelineOptions(
        streaming=True,
        save_main_session=True,
        runner='DataflowRunner',
        project=project_id,
        job_name=job_name,
        region='europe-west1',
        temp_location='gs://data-project-2/temp',
        staging_location='gs://data-project-2/staging',
        experiments=['use_runner_v2']
    )

    with beam.Pipeline(options=pipeline_options) as p:
        datos_ayuda = (
            p
            | "Leer datos de ayuda" >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_ayuda}")
            | "Decodificar mensajes de ayuda" >> beam.Map(DecodificarMensaje)
            | "Filtrar Nulos Ayuda" >> beam.Filter(lambda x: x is not None)
            | "Ventana fija de ayuda" >> beam.WindowInto(beam.window.FixedWindows(60))
        )

        datos_voluntarios = (
            p
            | "Leer datos de voluntarios" >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_voluntarios}")
            | "Decodificar mensajes de voluntarios" >> beam.Map(DecodificarMensaje)
            | "Filtrar Nulos Voluntarios" >> beam.Filter(lambda x: x is not None)
            | "Ventana fija de voluntarios" >> beam.WindowInto(beam.window.FixedWindows(60))
        )

        grouped_data = (
            {subscription_ayuda: datos_ayuda, subscription_voluntarios: datos_voluntarios}
            | "Juntar por necesidad" >> beam.CoGroupByKey()
        )

        resultados = (
            grouped_data
            | "Filtrar y Emparejar" >> beam.FlatMap(FiltrarYEmparejar).with_outputs(MATCHES_TAG, NO_MATCH_TAG)
        )

        matches_pcoll = resultados[MATCHES_TAG]
        no_matches_pcoll = resultados[NO_MATCH_TAG]

        schema_matches = {
            "fields": [
                {"name": "peticion", "type": "RECORD", "mode": "NULLABLE", "fields": [
                    {"name": "ID", "type": "STRING"},
                    {"name": "Nombre", "type": "STRING"},
                    {"name": "Nivel de Urgencia", "type": "STRING"},
                    {"name": "Necesidad", "type": "STRING"}
                ]},
                {"name": "voluntario", "type": "RECORD", "mode": "NULLABLE", "fields": [
                    {"name": "ID", "type": "STRING"},
                    {"name": "Nombre", "type": "STRING"},
                    {"name": "Nivel de Urgencias", "type": "STRING"},
                    {"name": "Necesidad", "type": "STRING"}
                ]}
            ]
        }

        schema_no_matches = {
            "fields": [
                {"name": "peticion", "type": "RECORD", "mode": "NULLABLE", "fields": [
                    {"name": "ID", "type": "STRING"},
                    {"name": "Nombre", "type": "STRING"},
                    {"name": "Nivel de Urgencia", "type": "STRING"},
                    {"name": "Necesidad", "type": "STRING"}
                ]}
            ]
        }

        matches_pcoll | "Guardar Matches en BQ" >> beam.io.WriteToBigQuery(
            table=f"{project_id}:{dataset_id}.{matches_table}",
            schema=schema_matches,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            batch_size=500
        )

        no_matches_pcoll | "Guardar No Matches en BQ" >> beam.io.WriteToBigQuery(
            table=f"{project_id}:{dataset_id}.{no_matches_table}",
            schema=schema_no_matches,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            batch_size=500
        )

logging.getLogger().setLevel(logging.INFO)
logging.info("Iniciando el proceso de Dataflow...")
run()
