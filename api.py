from fastapi import FastAPI
import json
import random
import time
from faker import Faker
from datetime import datetime
from google.cloud import pubsub_v1
import unidecode

# Configuración de Pub/Sub
PROJECT_ID = "data-project-2-449815"
TOPIC_REQUESTS = "ayuda"
TOPIC_HELPERS = "voluntarios"

publisher = pubsub_v1.PublisherClient()
topic_requests_path = publisher.topic_path(PROJECT_ID, TOPIC_REQUESTS)
topic_helpers_path = publisher.topic_path(PROJECT_ID, TOPIC_HELPERS)

app = FastAPI()

fake = Faker('es_ES')

urgencias = [ "Alta", "Media", "Baja"]
necesidades = ["Agua", "Comida", "Maquinaria Pesada", "Herramientas manuales", "Fontaneria", "Electricista", "Hogar", "Ropa", "Medicinas", "Limpieza"]
voluntario_disponibilidad = ["Inmediata", "Un café y voy", "Puede tardar"]

def generar_id_unico(prefix):
    return f"{prefix}{random.randint(1000, 100000)}"

def generar_timestamp():
    return datetime.utcnow().isoformat()

def generar_ubicacion():
    latitud = round(random.uniform(39.45, 39.50), 6)
    longitud = round(random.uniform(-0.40, -0.35), 6)
    return {"latitud": latitud, "longitud": longitud}

def normalizar_nombre(nombre):
    return unidecode.unidecode(nombre)

def enviar_a_pubsub(topic_path, mensaje):
    mensaje_json = json.dumps(mensaje).encode("utf-8")
    future = publisher.publish(topic_path, mensaje_json)
    future.result()
    return {"status": "success", "message": "Mensaje enviado"}

@app.post("/generate_requests")
def generate_requests(n: int = 1):
    peticiones = []
    for _ in range(n):
        peticion = {
            "ID": generar_id_unico("A"),
            "Nombre": normalizar_nombre(fake.name()),
            "Edad": random.randint(18, 80),
            "Telefono": str(random.randint(600000000, 699999999)),
            "Nivel_Urgencia": random.choice(urgencias),
            "Necesidad": random.choice(necesidades),
            "Timestamp": generar_timestamp(),
            "Ubicacion": generar_ubicacion()
        }
        enviar_a_pubsub(topic_requests_path, peticion)
        peticiones.append(peticion)
    return {"generated_requests": peticiones}

@app.post("/generate_helpers")
def generate_helpers(n: int = 1):
    voluntarios = []
    for _ in range(n):
        voluntario = {
            "ID": generar_id_unico("V"),
            "Nombre": normalizar_nombre(fake.name()),
            "Edad": random.randint(18, 80),
            "Telefono": str(random.randint(600000000, 699999999)),
            "Necesidad": random.choice(necesidades),
            "Nivel de Urgencias": random.choice(voluntario_disponibilidad),
            "Timestamp": generar_timestamp(),
            "Ubicacion": generar_ubicacion()
        }
        enviar_a_pubsub(topic_helpers_path, voluntario)
        voluntarios.append(voluntario)
    return {"generated_helpers": voluntarios}

@app.get("/")
def root():
    return {"message": "API para generación de datos aleatorios"}