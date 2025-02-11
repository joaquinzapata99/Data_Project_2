import apache_beam as beam
import json
from apache_beam.options.pipeline_options import PipelineOptions

# Configuración del proyecto
project_id = "data-project-2-449815"
subscription_ayuda = "ayuda-sub"
subscription_voluntarios = "voluntarios-sub"

# Tabla de correspondencia entre Nivel de Urgencia (Petición) y Nivel de Urgencias (Voluntario)
matching_criterios = {
    "Alta": ["Inmediata"],
    "Media": ["Un café y voy"],
    "Baja": ["Puede tardar"]
}

def DecodificarMensaje(msg):
    """Decodifica un mensaje Pub/Sub y lo convierte en JSON."""
    message = msg.decode("utf-8")
    decodificado = json.loads(message)
    return decodificado["Necesidad"], decodificado  # Agrupamos por Necesidad

class FiltrarMatchingPorUrgencia(beam.DoFn):
    """
    Empareja peticiones de ayuda con voluntarios según:
    - Necesidad (ya agrupada por CoGroupByKey)
    - Nivel de Urgencia (petición) vs Nivel de Urgencias (voluntario)
    """

    def process(self, elemento):
        necesidad, (solicitudes, voluntarios) = elemento  # Desempaquetar correctamente

        for solicitud in solicitudes:
            nivel_urgencia = solicitud["Nivel de Urgencia"]

            # Filtrar voluntarios compatibles según la tabla de matching
            voluntarios_compatibles = [
                v for v in voluntarios if v["Nivel de Urgencias"] in matching_criterios[nivel_urgencia]
            ]

            if voluntarios_compatibles:
                voluntario_asignado = voluntarios_compatibles[0]  # Tomamos el primer voluntario compatible
                yield beam.pvalue.TaggedOutput("matches", {
                    "Solicitud": solicitud,
                    "Voluntario": voluntario_asignado
                })
            else:
                yield beam.pvalue.TaggedOutput("no_matches", solicitud)  # Peticiones sin match

def run():
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
            | "Leer datos de ayuda" >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_ayuda}")
            | "Decodificar mensajes de ayuda" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de ayuda" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        datos_voluntarios = (
            p
            | "Leer datos de voluntarios" >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_voluntarios}")
            | "Decodificar mensajes de voluntarios" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de voluntarios" >> beam.WindowInto(beam.window.FixedWindows(20))
        )

        grouped_data = (
            (datos_ayuda, datos_voluntarios)
            | "Juntar por necesidad" >> beam.CoGroupByKey()
        )

        # Aplicar el DoFn para hacer el matching
        emparejamientos = grouped_data | "Filtrar Matching" >> beam.ParDo(FiltrarMatchingPorUrgencia()).with_outputs("matches", "no_matches")

        # Extraer cada PCollection
        matches = emparejamientos.matches
        no_matches = emparejamientos.no_matches

        # Printear resultados
        matches | "Print Matches" >> beam.Map(print)
        no_matches | "Print No Matches" >> beam.Map(print)

# Ejecutar el proceso
run()
