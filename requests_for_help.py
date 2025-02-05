import json
import random
import time
from faker import Faker
from datetime import datetime
from google.cloud import pubsub_v1
import unidecode

# Configuración de Pub/Sub
PROJECT_ID = "data-project-2-449815"
TOPIC_ID = "ayuda"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def generar_id_unico():
    """Genera un ID único que comienza con 'A' seguido de un número aleatorio único."""
    return f"A{random.randint(1000, 100000)}"

def generar_timestamp():
    """Genera un timestamp en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)."""
    return datetime.utcnow().isoformat()

def generar_ubicacion():
    """Genera coordenadas aleatorias dentro de Valencia."""
    latitud = round(random.uniform(39.45, 39.50), 6)
    longitud = round(random.uniform(-0.40, -0.35), 6)
    return {"latitud": latitud, "longitud": longitud}

def normalizar_nombre(nombre):
    """Elimina acentos y caracteres especiales del nombre."""
    return unidecode.unidecode(nombre)

def crear_peticiones(num_peticiones):
    """Genera una lista de peticiones de ayuda con datos aleatorios."""
    fake = Faker('es_ES')  
    urgencias = ["Muy urgente", "Alta", "Media", "Baja"]
    necesidades = ["Agua", "Comida", "Maquinaria Pesada", "Herramientas manuales", "Fontaneria", "Electricista", "Refugio", "Ropa", "Medicinas", "Limpieza"]

    peticiones = []
    for _ in range(num_peticiones):
        peticion = {
            "ID": generar_id_unico(),
            "Nombre": normalizar_nombre(fake.name()),
            "Edad": random.randint(18, 80),
            "Telefono": str(random.randint(600000000, 699999999)),
            "Nivel_Urgencia": random.choice(urgencias),
            "Necesidad": random.choice(necesidades),
            "Timestamp": generar_timestamp(),
            "Ubicacion": generar_ubicacion()
        }
        peticiones.append(peticion)

    return peticiones

def enviar_a_pubsub(mensaje):
    """Publica un mensaje en Pub/Sub."""
    mensaje_json = json.dumps(mensaje).encode("utf-8")
    future = publisher.publish(topic_path, mensaje_json)
    future.result()
    print(f"Mensaje enviado a Pub/Sub: {mensaje}")

if __name__ == "__main__":
    num_peticiones = 1000  # Número de peticiones a generar

    for _ in range(num_peticiones):
        peticion = crear_peticiones(1)[0]  # Genera una única petición
        enviar_a_pubsub(peticion)
        time.sleep(random.uniform(0.5, 2))  # Simula envíos en tiempo real

    print("Todas las peticiones han sido enviadas a Pub/Sub.")
