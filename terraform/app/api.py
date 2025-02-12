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
voluntario_disponibilidad = ["Inmediata", "Un cafe y voy", "Puede tardar"]
urgencias = ["Baja", "Media", "Alta"]

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

def enviar_a_pubsub(topic_path, mensajes):
    """Publica mensajes en Pub/Sub en un batch."""
    try:
        futures = []
        for mensaje in mensajes:
            mensaje_json = json.dumps(mensaje).encode("utf-8")
            future = publisher.publish(topic_path, mensaje_json)
            futures.append(future)

        # Esperar confirmación de publicación
        for future in futures:
            future.result()
    except Exception as e:
        print(f"Error al enviar mensaje a Pub/Sub: {e}")

def generar_datos_automaticamente():
    """Genera solicitudes de ayuda y voluntarios de forma continua, pero desfasados y desbalanceados."""
    print("Generando datos con desbalance...")

    while True:
        # 1) Generar un batch grande de peticiones
        batch_requests = [
            {
                "ID": generar_id_unico("A"),
                "Nombre": normalizar_nombre(fake.name()),
                "Edad": random.randint(18, 80),
                "Telefono": str(random.randint(600000000, 699999999)),
                "Necesidad": random.choice(necesidades),
                "Nivel de Urgencia": random.choice(urgencias),
                "Timestamp": generar_timestamp(),
                "Ubicacion": generar_ubicacion()
            }
            for _ in range(100)  # 100 peticiones
        ]

        # Enviar solo peticiones
        enviar_a_pubsub(topic_requests_path, batch_requests)
        print(f"Enviadas {len(batch_requests)} peticiones")

        # 2) Esperar un poco para que esas peticiones se "acumulen" solas en la ventana
        time.sleep(3)

        # 3) Generar un batch más pequeño de voluntarios
        batch_helpers = [
            {
                "ID": generar_id_unico("V"),
                "Nombre": normalizar_nombre(fake.name()),
                "Edad": random.randint(18, 80),
                "Telefono": str(random.randint(600000000, 699999999)),
                "Necesidad": random.choice(necesidades),
                "Nivel de Urgencias": random.choice(voluntario_disponibilidad),
                "Timestamp": generar_timestamp(),
                "Ubicacion": generar_ubicacion()
            }
            for _ in range(20)  # 20 voluntarios (menos que 100)
        ]

        # Enviar voluntarios
        enviar_a_pubsub(topic_helpers_path, batch_helpers)
        print(f"Enviados {len(batch_helpers)} voluntarios")

        # 4) Otra espera corta antes de la siguiente iteración
        time.sleep(1)

# Iniciar la generación automática en un hilo separado para no bloquear FastAPI
threading.Thread(target=generar_datos_automaticamente, daemon=True).start()

@app.get("/")
def root():
    return {"message": "API para generación de datos aleatorios desbalanceados"}
