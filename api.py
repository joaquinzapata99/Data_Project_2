from fastapi import FastAPI
import json
import random
import time
import threading
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

necesidades = ["Comida y Agua", "Medicinas", "Maquinaria Pesada"]
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
    try:
        mensaje_json = json.dumps(mensaje).encode("utf-8")
        future = publisher.publish(topic_path, mensaje_json)
        future.result()  # Espera a que se publique correctamente
    except Exception as e:
        print(f"Error al enviar mensaje a Pub/Sub: {e}")

def generar_datos_automaticamente():
    """Genera solicitudes de ayuda y voluntarios de forma automática en lotes."""
    max_requests = 10000
    max_helpers = 10000
    requests_generated = 0
    helpers_generated = 0

    print(f"Generando datos aleatorios hasta llegar a {max_requests} peticiones y {max_helpers} voluntarios...")

    while requests_generated < max_requests or helpers_generated < max_helpers:
        if requests_generated < max_requests:
            batch_requests = []
            for _ in range(100):  # Genera 100 solicitudes por iteración
                batch_requests.append({
                    "ID": generar_id_unico("A"),
                    "Nombre": normalizar_nombre(fake.name()),
                    "Edad": random.randint(18, 80),
                    "Telefono": str(random.randint(600000000, 699999999)),
                    "Necesidad": random.choice(necesidades),
                    "Timestamp": generar_timestamp(),
                    "Ubicacion": generar_ubicacion()
                })
            
            for peticion in batch_requests:
                enviar_a_pubsub(topic_requests_path, peticion)

            requests_generated += 100  # Ahora el contador aumenta correctamente
            print(f"Peticiones generadas: {requests_generated}")

        if helpers_generated < max_helpers:
            batch_helpers = []
            for _ in range(100):  # Genera 100 voluntarios por iteración
                batch_helpers.append({
                    "ID": generar_id_unico("V"),
                    "Nombre": normalizar_nombre(fake.name()),
                    "Edad": random.randint(18, 80),
                    "Telefono": str(random.randint(600000000, 699999999)),
                    "Necesidad": random.choice(necesidades),
                    "Nivel de Urgencias": random.choice(voluntario_disponibilidad),
                    "Timestamp": generar_timestamp(),
                    "Ubicacion": generar_ubicacion()
                })
            
            for voluntario in batch_helpers:
                enviar_a_pubsub(topic_helpers_path, voluntario)

            helpers_generated += 100  # Ahora el contador aumenta correctamente
            print(f"Voluntarios generados: {helpers_generated}")

        time.sleep(2)  # Espera 2 segundos antes de la siguiente iteración

    print("Generación completa.")

# Iniciar la generación automática en un hilo separado para no bloquear FastAPI
threading.Thread(target=generar_datos_automaticamente, daemon=True).start()

@app.get("/")
def root():
    return {"message": "API para generación de datos aleatorios"}
