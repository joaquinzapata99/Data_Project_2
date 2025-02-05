import json
import random
from faker import Faker
from datetime import datetime, time

def generar_hora_aleatoria():
    """Genera una hora aleatoria entre las 14:00 y 22:59:59."""
    hora = random.randint(14, 22)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    return time(hora, minuto, segundo).strftime("%H:%M:%S")

def creador_personas(num_gente):
    fake = Faker('es_ES')  
    people_data = []

    Urgencia = ["Alta", "Media", "Baja"] #Definir nivel de urgencia
    Necesidades = ["Agua", "Comida", "Maquinaria Pesada"] #ver mas necesidades

    for _ in range(num_gente):
        person = {
            "Nombre": fake.name(),
            "Edad": random.randint(18, 65),  
            "Numero_de_teléfono": str(random.randint(600000000, 699999999)),
            "Nivel_de_Urgencia": random.choice(Urgencia),
            "Necesidad": random.choice(Necesidades),
            "Hora_de_ayuda": generar_hora_aleatoria()
        }
        people_data.append(person)

    return people_data


if __name__ == "__main__":
    num_gente = 100 
    people = creador_personas(num_gente)

    # Save to JSON file
    with open("Generador_personas.json", "w", encoding="utf-8") as json_file:
        json.dump(people, json_file, ensure_ascii=False, indent=4)

    print("JSON file created.")