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
import os

# Configurar credenciales de BigQuery
st.set_page_config(page_title="BigQuery Streamlit Dashboard", layout="wide")

st.title("Resqlink: Plataforma de Voluntariado y Ayuda")

# Inicializar cliente de BigQuery
client = bigquery.Client()

# Se leen las variables de entorno
PROJECT_ID = os.getenv("PROJECT_ID", "data-project-2-449815")
TOPIC_VOLUNTARIOS = os.getenv("TOPIC_VOLUNTARIOS", "voluntarios-streamlit")
TOPIC_AFECTADOS = os.getenv("TOPIC_AFECTADOS", "ayuda-streamlit")
publisher = pubsub_v1.PublisherClient()

def obtener_info_contacto(match_id):
    """Obtiene la información de contacto para un match específico."""
    QUERY = """
    SELECT 
        m.Solicitud_ID,
        m.Voluntario_ID,
        s.Solicitud_Nombre as Solicitante_Nombre,
        s.Solicitud_Telefono as Solicitante_Telefono,
        v.Voluntario_Nombre as Voluntario_Nombre,
        v.Voluntario_Telefono as Voluntario_Telefono,
        m.Voluntario_Necesidad
    FROM `data-project-2-449815.dataflow_matches.match` m
    LEFT JOIN `data-project-2-449815.dataflow_matches.match` s
    ON m.Solicitud_ID = s.Solicitud_ID
    LEFT JOIN `data-project-2-449815.dataflow_matches.match` v
    ON m.Voluntario_ID = v.Voluntario_ID
    WHERE m.Solicitud_ID = @id OR m.Voluntario_ID = @id
    LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", match_id)
        ]
    )
    
    try:
        query_job = client.query(QUERY, job_config=job_config)
        results = query_job.to_dataframe()
        if not results.empty:
            return results.iloc[0]
        return None
    except Exception as e:
        st.error(f"Error al obtener información de contacto: {e}")
        return None

def generar_id_unico(prefix):
    return f"{prefix}{random.randint(1000, 100000)}"

def enviar_a_pubsub(topic, datos):
    """Envía un mensaje a Pub/Sub con los datos del formulario."""
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    mensaje_json = json.dumps(datos).encode("utf-8")
    future = publisher.publish(topic_path, mensaje_json)
    future.result()

# Definir las pestañas de la aplicación
menu = ["Encuesta Voluntarios", "Encuesta Afectados", "Mapa de Solicitudes y Voluntarios", 
        "Ver Todos los Matches", "Ver Información de Contacto"]
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

elif choice == "Ver Todos los Matches":
    st.title("Actividad de Matches en Vivo")
    
    refresh_interval = st.sidebar.slider("Intervalo de actualización (segundos)", 1, 30, 3)
    st_autorefresh(interval=refresh_interval * 1000, key="live_matches_recarga")
    
    if 'last_seen_matches' not in st.session_state:
        st.session_state.last_seen_matches = 0
    
    QUERY_ALL_MATCHES = """
        SELECT 
            Solicitud_ID, 
            Voluntario_ID, 
            Voluntario_Necesidad,
            Solicitud_Timestamp,
            Solicitud_Lat, 
            Solicitud_Lng, 
            Voluntario_Lat, 
            Voluntario_Lng
        FROM `data-project-2-449815.dataflow_matches.match`
        ORDER BY Solicitud_Timestamp DESC
        LIMIT 50
    """
    
    try:
        data_all_matches = client.query(QUERY_ALL_MATCHES).to_dataframe()
        
        if not data_all_matches.empty:
            data_all_matches['Solicitud_Timestamp'] = pd.to_datetime(data_all_matches['Solicitud_Timestamp'])
            data_all_matches['Fecha_Hora'] = data_all_matches['Solicitud_Timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')
            data_all_matches['Tiempo_Relativo'] = (datetime.datetime.utcnow() - data_all_matches['Solicitud_Timestamp']).apply(lambda x: f"{x.seconds // 60} min" if x.days == 0 else f"{x.days} días")
            
            total_matches = len(data_all_matches)
            nuevos_matches = total_matches - st.session_state.last_seen_matches
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de matches", total_matches)
            with col2:
                if nuevos_matches > 0:
                    st.metric("Nuevos matches", nuevos_matches, f"+{nuevos_matches}")
            
            st.session_state.last_seen_matches = total_matches
                
            st.subheader("Actividad de Matches en Tiempo Real")
            
            for i, row in data_all_matches.head(15).iterrows():
                es_nuevo = (datetime.datetime.utcnow() - row['Solicitud_Timestamp']).total_seconds() < 60
                
                with st.container():
                    if es_nuevo:
                        st.markdown(f"""
                            <div style='padding: 15px; border-radius: 10px; background-color: #28a745; color: white; margin-bottom: 10px; border: 1px solid #ddd;'>
                                <h3>¡NUEVO MATCH! 🎉</h3>
                                <p><strong>Hace:</strong> {row['Tiempo_Relativo']}</p>
                                <p><strong>Solicitud ID:</strong> {row['Solicitud_ID']}</p>
                                <p><strong>Voluntario ID:</strong> {row['Voluntario_ID']}</p>
                                <p><strong>Tipo de Ayuda:</strong> {row['Voluntario_Necesidad']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style='padding: 15px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 10px; border: 1px solid #ddd;'>
                                <p><strong>Match hace:</strong> {row['Tiempo_Relativo']}</p>
                                <p><strong>Solicitud ID:</strong> {row['Solicitud_ID']} - <strong>Voluntario ID:</strong> {row['Voluntario_ID']}</p>
                                <p><strong>Tipo de Ayuda:</strong> {row['Voluntario_Necesidad']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.subheader("Actividad de las Últimas 24 Horas")
            
            last_24h = data_all_matches[data_all_matches['Solicitud_Timestamp'] > (datetime.datetime.utcnow() - datetime.timedelta(hours=24))]
            
            if not last_24h.empty:
                last_24h['Hora'] = last_24h['Solicitud_Timestamp'].dt.floor('H')
                matches_por_hora = last_24h.groupby('Hora').size().reset_index(name='Cantidad')
                matches_por_hora = matches_por_hora.set_index('Hora')
                
                idx = pd.date_range(end=datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0),
                                   periods=24, freq='H')
                matches_por_hora = matches_por_hora.reindex(idx, fill_value=0)
                
                st.line_chart(matches_por_hora['Cantidad'])
            else:
                st.info("No hay datos de matches en las últimas 24 horas.")
                
        else:
            st.info("Esperando nuevos matches... La información se actualizará automáticamente.")
            
    except Exception as e:
        st.error(f"Error al obtener datos de BigQuery: {e}")
        st.exception(e)

elif choice == "Ver Información de Contacto":
    st.title("Información de Contacto de Match")
    
    match_id = st.text_input("Ingrese su ID de Voluntario o Solicitud:", "")
    
    if st.button("Buscar Información de Contacto"):
        if match_id:
            info = obtener_info_contacto(match_id)
            if info is not None:
                st.markdown("""
                    <style>
                    .contact-info {
                        padding: 20px;
                        border-radius: 10px;
                        background-color: #f8f9fa;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                    }
                    .contact-header {
                        color: #1f77b4;
                        font-size: 1.2em;
                        margin-bottom: 10px;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Información del Solicitante
                st.markdown("""
                    <div class="contact-info">
                        <div class="contact-header">📋 Información del Solicitante</div>
                        <p><strong>ID:</strong> {}</p>
                        <p><strong>Nombre:</strong> {}</p>
                        <p><strong>Teléfono:</strong> {}</p>
                    </div>
                """.format(
                    info['Solicitud_ID'],
                    info['Solicitante_Nombre'],
                    info['Solicitante_Telefono']
                ), unsafe_allow_html=True)
                
                # Información del Voluntario
                st.markdown("""
                    <div class="contact-info">
                        <div class="contact-header">🤝 Información del Voluntario</div>
                        <p><strong>ID:</strong> {}</p>
                        <p><strong>Nombre:</strong> {}</p>
                        <p><strong>Teléfono:</strong> {}</p>
                    </div>
                """.format(
                    info['Voluntario_ID'],
                    info['Voluntario_Nombre'],
                    info['Voluntario_Telefono']
                ), unsafe_allow_html=True)
                
                # Detalles del Match
                st.markdown("""
                    <div class="contact-info">
                        <div class="contact-header">ℹ️ Detalles del Match</div>
                        <p><strong>Tipo de Ayuda:</strong> {}</p>
                    </div>
                """.format(info['Voluntario_Necesidad']), unsafe_allow_html=True)
                
                # Instrucciones de seguridad
                st.warning("""
                    🔒 Por su seguridad:
                    - Verifique la identidad de la persona antes de encontrarse
                    - Reúnase en lugares públicos y seguros
                    - Mantenga un registro de sus comunicaciones
                    - Si algo no parece correcto, repórtelo inmediatamente
                """)
            else:
                st.error("No se encontró información para el ID proporcionado o aún no tiene un match.")
        else:
            st.warning("Por favor, ingrese un ID para buscar.")