import streamlit as st
from google.cloud import bigquery, pubsub_v1
import pandas as pd
import pydeck as pdk
import random
import math
import datetime
import json
import time
from streamlit_autorefresh import st_autorefresh

# Configuración de la página
st.set_page_config(page_title="BigQuery Streamlit Dashboard", layout="wide")

st.title("BigQuery Plataforma de Voluntariado y Ayuda")

# Configurar clientes de Google Cloud (BigQuery y Pub/Sub)
PROJECT_ID = "data-project-2-449815"
TOPIC_VOLUNTARIOS = "voluntarios-streamlit"
TOPIC_AFECTADOS = "ayuda-streamlit"

try:
    client = bigquery.Client()  # Autenticación automática en Cloud Run
    publisher = pubsub_v1.PublisherClient()
    st.success("Conectado a Google Cloud correctamente 🎉")
except Exception as e:
    st.error(f"Error al conectar con Google Cloud: {e}")
    st.stop()

# Opciones predefinidas
necesidades = ["Comida y Agua", "Medicinas", "Maquinaria Pesada", "Refugio Temporal", "Ropa", "Ayuda a animales"]
voluntario_disponibilidad = ["Inmediata", "Un café y voy", "Puede tardar"]
urgencias = ["Baja", "Media", "Alta"]

# Generar ID único
def generar_id_unico(prefix):
    return f"{prefix}{random.randint(1000, 100000)}"

# Enviar datos a Pub/Sub
def enviar_a_pubsub(topic, datos):
    try:
        topic_path = publisher.topic_path(PROJECT_ID, topic)
        mensaje_json = json.dumps(datos).encode("utf-8")
        future = publisher.publish(topic_path, mensaje_json)
        future.result()
        st.success(f"Datos enviados correctamente al tópico {topic}")
    except Exception as e:
        st.error(f"Error al enviar mensaje a Pub/Sub: {e}")

# Generar ubicación aleatoria en Valencia
def generar_ubicacion():
    centro_latitud = 39.4699
    centro_longitud = -0.3763
    radio_km = 3
    radio_grados = radio_km / 111  # 1 grado ≈ 111 km
    angulo = random.uniform(0, 2 * math.pi)
    radio = random.uniform(0, radio_grados)
    latitud = centro_latitud + (radio * math.cos(angulo))
    longitud = centro_longitud + (radio * math.sin(angulo)) / math.cos(math.radians(centro_latitud))
    return {"latitud": round(latitud, 6), "longitud": round(longitud, 6)}

# Buscar ID en BigQuery
def buscar_id_en_bigquery(id_usuario):
    consultas = {
        "Matches": "SELECT * FROM `data-project-2-449815.dataflow_matches.match` WHERE Solicitud_ID = @id OR Voluntario_ID = @id",
        "Voluntarios sin Match": "SELECT * FROM `data-project-2-449815.dataflow_matches.no_match_voluntarios` WHERE Voluntario_ID = @id",
        "Solicitudes sin Match": "SELECT * FROM `data-project-2-449815.dataflow_matches.no_matches_solicitudes` WHERE Solicitud_ID = @id",
    }

    resultados = {}
    encontrado = False

    for nombre_tabla, query in consultas.items():
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", id_usuario)]
            )
            query_job = client.query(query, job_config=job_config)
            df = query_job.to_dataframe()
            if not df.empty:
                encontrado = True
            resultados[nombre_tabla] = df
        except Exception as e:
            st.error(f"Error en consulta a BigQuery ({nombre_tabla}): {e}")

    return resultados if encontrado else "⚠️ Este ID aún está en proceso. Inténtalo más tarde."

# ---------------------- Aplicación Streamlit ----------------------
menu = ["Encuesta Voluntarios", "Encuesta Afectados", "Mapa de Solicitudes y Voluntarios", "Consulta por tu ID", "Ver Todos los Matches"]
choice = st.sidebar.selectbox("Selecciona una opción", menu)

if choice == "Encuesta Voluntarios":
    st.subheader("Formulario para Voluntarios")
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", min_value=18, max_value=90, step=1)
    telefono = st.text_input("Teléfono de Contacto")
    necesidad = st.selectbox("¿Qué tipo de ayuda puedes ofrecer?", necesidades)
    disponibilidad = st.selectbox("Disponibilidad para ayudar", voluntario_disponibilidad)

    if st.button("Enviar Datos"):
        datos = {
            "ID": generar_id_unico('V'),
            "Nombre": nombre,
            "Edad": edad,
            "Telefono": telefono,
            "Necesidad": necesidad,
            "Nivel de Urgencia": disponibilidad,
            "Timestamp": datetime.datetime.utcnow().isoformat(),
            "Ubicacion": generar_ubicacion()
        }
        enviar_a_pubsub(TOPIC_VOLUNTARIOS, datos)

elif choice == "Encuesta Afectados":
    st.subheader("Formulario para Afectados")
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", min_value=18, max_value=90, step=1)
    telefono = st.text_input("Teléfono de Contacto")
    necesidad = st.selectbox("¿Qué tipo de ayuda necesitas?", necesidades)
    urgencia = st.selectbox("Nivel de urgencia", urgencias)

    if st.button("Enviar Datos"):
        datos = {
            "ID": generar_id_unico('A'),
            "Nombre": nombre,
            "Edad": edad,
            "Telefono": telefono,
            "Necesidad": necesidad,
            "Nivel de Urgencia": urgencia,
            "Timestamp": datetime.datetime.utcnow().isoformat(),
            "Ubicacion": generar_ubicacion()
        }
        enviar_a_pubsub(TOPIC_AFECTADOS, datos)

elif choice == "Consulta por tu ID":
    st.title("Consultar ID en BigQuery")
    id_usuario = st.text_input("Ingrese su ID:", "")

    if st.button("Buscar ID"):
        if id_usuario:
            resultados = buscar_id_en_bigquery(id_usuario)
            if isinstance(resultados, str):
                st.warning(resultados)
            else:
                for nombre_tabla, df in resultados.items():
                    st.subheader(f"Resultados en {nombre_tabla}")
                    if df.empty:
                        st.write("No se encontraron resultados.")
                    else:
                        st.dataframe(df)
        else:
            st.warning("Por favor, ingrese un ID antes de buscar.")

elif choice == "Ver Todos los Matches":
    st.title("Actividad de Matches en Vivo")
    st_autorefresh(interval=5000, key="live_matches_recarga")

    QUERY_ALL_MATCHES = """
        SELECT Solicitud_ID, Voluntario_ID, Voluntario_Necesidad, Solicitud_Timestamp
        FROM `data-project-2-449815.dataflow_matches.match`
        ORDER BY Solicitud_Timestamp DESC
        LIMIT 50
    """

    try:
        data_all_matches = client.query(QUERY_ALL_MATCHES).to_dataframe()
        if not data_all_matches.empty:
            st.subheader("Últimos Matches")
            st.dataframe(data_all_matches)
        else:
            st.info("Esperando nuevos matches... Se actualizará automáticamente.")
    except Exception as e:
        st.error(f"Error al obtener datos de BigQuery: {e}")

