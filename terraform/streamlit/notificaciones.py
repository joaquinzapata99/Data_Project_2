import os
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

# Configurar credenciales de BigQuery
st.set_page_config(page_title="BigQuery Streamlit Dashboard", layout="wide")

st.title("BigQuery Plataforma de Voluntariado y Ayuda")

# Definir la ruta del JSON en el código
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "prueba.json"

# Inicializar cliente de BigQuery
client = bigquery.Client()

# Configurar Pub/Sub
PROJECT_ID = "data-project-2-449815"
TOPIC_VOLUNTARIOS = "voluntarios-streamlit"
TOPIC_AFECTADOS = "ayuda-streamlit"

publisher = pubsub_v1.PublisherClient()

def generar_id_unico(prefix):
    return f"{prefix}{random.randint(1000, 100000)}"

def enviar_a_pubsub(topic, datos):
    """Envía un mensaje a Pub/Sub con los datos del formulario."""
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    mensaje_json = json.dumps(datos).encode("utf-8")
    future = publisher.publish(topic_path, mensaje_json)
    future.result()

# Definir las pestañas de la aplicación
menu = ["Encuesta Voluntarios", "Encuesta Afectados", "Mapa de Solicitudes y Voluntarios", "Consulta por tu ID"]
choice = st.sidebar.selectbox("Selecciona una opción", menu)

# Opciones predefinidas
necesidades = ["Comida y Agua", "Medicinas", "Maquinaria Pesada", "Refugio Temporal", "Ropa", "Ayuda a animales"] 
voluntario_disponibilidad = ["Inmediata", "Un café y voy", "Puede tardar"]
urgencias = ["Baja", "Media", "Alta"]

# Colores fijos para los matches
colores = {
    0: [255, 0, 0, 255],  # Rojo
    1: [0, 0, 255, 255],  # Azul
    2: [0, 128, 0, 255]   # Verde oscuro
}

def generar_id_unico(prefix):
    return f"{prefix}{random.randint(1000, 100000)}"

def buscar_id_en_bigquery(id_usuario):
    consultas = {
        "Matches": "SELECT * FROM `data-project-2-449815.dataflow_matches.match` WHERE Solicitud_ID = @id OR Voluntario_ID = @id",
        "Voluntarios sin Match": "SELECT * FROM `data-project-2-449815.dataflow_matches.no_match_voluntarios` WHERE Voluntario_ID = @id",
        "Solicitudes sin Match": "SELECT * FROM `data-project-2-449815.dataflow_matches.no_matches_solicitudes` WHERE Solicitud_ID = @id",
    }

    resultados = {}
    encontrado = False  # Variable para rastrear si encontramos el ID

    for nombre_tabla, query in consultas.items():
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", id_usuario)]
        )
        query_job = client.query(query, job_config=job_config)
        df = query_job.to_dataframe()

        if not df.empty:
            encontrado = True  # Se encontró el ID en alguna tabla

        resultados[nombre_tabla] = df

    if not encontrado:
        return "⚠️ Este ID aún está en proceso. Inténtalo más tarde."

    return resultados

def generar_ubicacion():
    """Genera una ubicación aleatoria dentro de un radio de 3 km en Valencia."""
    centro_latitud = 39.4699
    centro_longitud = -0.3763
    radio_km = 3
    radio_grados = radio_km / 111  # Aproximación: 1 grado ≈ 111 km
    angulo = random.uniform(0, 2 * math.pi)
    radio = random.uniform(0, radio_grados)
    latitud = centro_latitud + (radio * math.cos(angulo))
    longitud = centro_longitud + (radio * math.sin(angulo)) / math.cos(math.radians(centro_latitud))
    return {"latitud": round(latitud, 6), "longitud": round(longitud, 6)}

# -------------------------- Aplicación Principal --------------------------
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
            "Nivel de Urgencias": disponibilidad,
            "Timestamp": datetime.datetime.utcnow().isoformat(),
            "Ubicacion": generar_ubicacion()
        }
        enviar_a_pubsub(TOPIC_VOLUNTARIOS, datos)
        st.success(f"Tu solicitud con ID {datos['ID']} ha sido enviada correctamente.")

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
        st.success(f"Tu solicitud con ID {datos['ID']} ha sido enviada correctamente.")

elif choice == "Mapa de Solicitudes y Voluntarios":
    # Agregar un temporizador que recarga la página cada 5 segundos
    st_autorefresh(interval=5000, key="mapa_recarga")

    st.subheader("Últimos 3 Matches")

    QUERY_RECENT = """
        SELECT Solicitud_ID, Voluntario_ID, Voluntario_Necesidad, 
               Solicitud_Lat, Solicitud_Lng, Voluntario_Lat, Voluntario_Lng 
        FROM `data-project-2-449815.dataflow_matches.match`
        ORDER BY Solicitud_Timestamp DESC
        LIMIT 3
    """

    try:
        data_recent = client.query(QUERY_RECENT).to_dataframe()
    except Exception as e:
        st.error(f"Error al obtener datos de BigQuery: {e}")
        data_recent = pd.DataFrame()

    # Mostrar detalles de los matches
    if not data_recent.empty:
        st.subheader("Detalles de los Últimos 3 Matches")

        with st.container():
            for i, row in data_recent.iterrows():
                color = colores.get(i, [128, 128, 128, 255])  # Gris por defecto si no hay color asignado
                color_hex = f"rgb({color[0]}, {color[1]}, {color[2]})"
                st.markdown(f"""
                    <div style='padding: 10px; border-radius: 10px; background-color: {color_hex}; color: white; margin-bottom: 10px; border: 1px solid #ddd;'>
                        ✅ <strong>Se ha producido un match:</strong> La solicitud con ID <strong>{row['Solicitud_ID']}</strong> ha encontrado un voluntario con ID <strong>{row['Voluntario_ID']}</strong> para la necesidad de <strong>{row['Voluntario_Necesidad']}</strong>.
                    </div>
                """, unsafe_allow_html=True)

    # Mostrar el mapa
    if not data_recent.empty:
        data_recent["color"] = data_recent.index.map(lambda i: colores.get(i, [128, 128, 128, 255]))

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=data_recent[["Solicitud_Lat", "Voluntario_Lat"]].mean().mean(),
                longitude=data_recent[["Solicitud_Lng", "Voluntario_Lng"]].mean().mean(),
                zoom=12,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data_recent,
                    get_position=["Solicitud_Lng", "Solicitud_Lat"],
                    get_radius=100,
                    get_color="color",
                    pickable=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data_recent,
                    get_position=["Voluntario_Lng", "Voluntario_Lat"],
                    get_radius=100,
                    get_color="color",
                    pickable=True,
                )
            ]
        ))
    else:
        st.warning("No se encontraron datos para visualizar.")

elif choice == "Consulta por tu ID":
    st.title("Consultar ID en BigQuery")

    id_usuario = st.text_input("Ingrese su ID:", "")

    if st.button("Buscar ID"):
        if id_usuario:
            resultados = buscar_id_en_bigquery(id_usuario)

            if isinstance(resultados, str):  # Si la función devuelve un mensaje en lugar de un diccionario
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
