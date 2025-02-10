import apache_beam as beam
from apache_beam.runners import DataflowRunner
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam.transforms.window as window
from apache_beam.metrics import Metrics

# B. Apache Beam ML Libraries
from apache_beam.ml.inference.base import ModelHandler
from apache_beam.ml.inference.base import RunInference
from apache_beam.runners.interactive.interactive_runner import InteractiveRunner
import apache_beam.runners.interactive.interactive_beam as ib

# C. Python Libraries
from datetime import datetime
import argparse
import logging
import json

# Import libraries
from google.cloud import pubsub_v1
from google.pubsub_v1.types import Encoding
import logging
import sys
import pandas as pd

sys.argv = sys.argv[:1]


beam.options.pipeline_options.PipelineOptions.allow_non_parallel_instruction_output = True
DataflowRunner.test = False

project_id = "data-project-2-449815"
subscription_ayuda = "ayuda-sub"
subscription_voluntarios = "voluntarios-sub"



def DecodificarMensaje(msg):
    """Decodifica un mensaje Pub/Sub y lo convierte en JSON."""
    message = msg.decode("utf-8")
    decodificado = json.loads(message)
    return decodificado["Necesidad"], decodificado



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
        # Leer datos de ayuda
        datos_ayuda = (
            p
            | "Leer datos de ayuda"
            >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_ayuda}")
            | "Decodificar mensajes de ayuda" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de ayuda" >> beam.WindowInto(beam.window.FixedWindows(20))
        )
        
        # Leer datos de voluntarios
        datos_voluntarios = (
            p
            | "Leer datos de voluntarios"
            >> beam.io.ReadFromPubSub(subscription=f"projects/{project_id}/subscriptions/{subscription_voluntarios}")
            | "Decodificar mensajes de voluntarios" >> beam.Map(DecodificarMensaje)
            | "Ventana fija de voluntarios" >> beam.WindowInto(beam.window.FixedWindows(20))
        )
        
        # Agrupar por necesidad
        grouped_data = (
            (datos_ayuda, datos_voluntarios)
            | "Juntar por necesidad" >> beam.CoGroupByKey()
        )
    
        leer_mensajes = (
            grouped_data
            | "PrintMessage" >> beam.Map(print) 
        )

# Ejecutar el proceso
logging.getLogger().setLevel(logging.INFO)
logging.info("El proceso ha comenzado")
run()