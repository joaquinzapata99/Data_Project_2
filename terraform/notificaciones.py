import os
import streamlit as st
from google.cloud import bigquery
import pandas as pd
import pydeck as pdk

# Configurar credenciales de BigQuery
st.set_page_config(page_title="BigQuery Streamlit Dashboard", layout="wide")
st.title("BigQuery Match Notifications y Mapas de Ubicaciones")

# Definir la ruta del JSON en el código
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "prueba.json"

# Inicializar cliente de BigQuery
client = bigquery.Client()

# Consulta SQL para obtener los 3 matches más recientes
QUERY_RECENT = """
    SELECT Solicitud_ID, Voluntario_ID, Voluntario_Necesidad, 
           Solicitud_Lat, Solicitud_Lng, Voluntario_Lat, Voluntario_Lng 
    FROM `data-project-2-449815.dataflow_matches.match`
    ORDER BY Solicitud_Timestamp DESC
    LIMIT 3
"""

# Consulta SQL para obtener todos los registros
QUERY_ALL = """
    SELECT Solicitud_ID, Voluntario_ID, Voluntario_Necesidad, 
           Solicitud_Lat, Solicitud_Lng, Voluntario_Lat, Voluntario_Lng 
    FROM `data-project-2-449815.dataflow_matches.match`
"""

def get_data(query):
    """Ejecuta la consulta en BigQuery y devuelve un DataFrame."""
    query_job = client.query(query)
    df = query_job.to_dataframe()
    return df

# Obtener datos recientes y globales
data_recent = get_data(QUERY_RECENT)
data_all = get_data(QUERY_ALL)

st.subheader("Últimos 3 Matches")
with st.container():
    for index, row in data_recent.iterrows():
        st.markdown(f"""
            <div style='padding: 10px; border-radius: 10px; background-color: #f8f9fa; color: black; margin-bottom: 10px; border: 1px solid #ddd;'>
                ✅ <strong>Se ha producido un match:</strong> La solicitud con ID <strong>{row['Solicitud_ID']}</strong> ha encontrado un voluntario con ID <strong>{row['Voluntario_ID']}</strong> para darse la <strong>{row['Voluntario_Necesidad']}</strong>.
            </div>
        """, unsafe_allow_html=True)

# Mostrar mapa con solo las 3 últimas solicitudes y voluntarios
st.subheader("Mapa de los Últimos 3 Matches")
if not data_recent.empty:
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
                get_color=[255, 0, 0, 255],  # Rojo para solicitudes
                pickable=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data_recent,
                get_position=["Voluntario_Lng", "Voluntario_Lat"],
                get_radius=100,
                get_color=[0, 100, 0, 255],  # Verde oscuro para voluntarios
                pickable=True,
            )
        ]
    ))

# Mostrar mapa con todas las solicitudes y voluntarios
st.subheader("Mapa Global de Solicitudes y Voluntarios")
if not data_all.empty:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=pdk.ViewState(
            latitude=data_all[["Solicitud_Lat", "Voluntario_Lat"]].mean().mean(),
            longitude=data_all[["Solicitud_Lng", "Voluntario_Lng"]].mean().mean(),
            zoom=10,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data_all,
                get_position=["Solicitud_Lng", "Solicitud_Lat"],
                get_radius=40,
                get_color=[255, 0, 0, 200],  # Rojo semi-transparente para solicitudes
                pickable=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data_all,
                get_position=["Voluntario_Lng", "Voluntario_Lat"],
                get_radius=40,
                get_color=[0, 100, 0, 200],  # Verde oscuro semi-transparente para voluntarios
                pickable=True,
            )
        ]
    ))
