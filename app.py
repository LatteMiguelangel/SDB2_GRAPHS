# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from services.routing import obtener_ruta_optima, obtener_nodos_por_tipo

# Configuración de la página
st.set_page_config(page_title="Logistics Optimizer", layout="wide")
st.title("🚚 Proyecto III: Smart Routing Optimizer")
st.markdown("Sistema de enrutamiento logístico basado en **Neo4j** y **Graph Data Science**.")

# --- INICIALIZAR LA MEMORIA DE LA SESIÓN ---
# Esto evita que los datos se borren al recargar la página
if 'ruta_calculada' not in st.session_state:
    st.session_state.ruta_calculada = False
if 'datos_ruta' not in st.session_state:
    st.session_state.datos_ruta = None

# --- BARRA LATERAL (Controles) ---
st.sidebar.header("Configuración de la Ruta")

# Obtener listas de nodos desde la BD
try:
    almacenes = obtener_nodos_por_tipo("Almacén")
    puntos = obtener_nodos_por_tipo("PuntoEntrega")
except Exception as e:
    st.error("Error conectando a Neo4j. Verifica tus credenciales en el archivo .env.")
    st.stop()

origen = st.sidebar.selectbox("Seleccione Almacén de Origen:", almacenes)
destino = st.sidebar.selectbox("Seleccione Punto de Destino:", puntos)
peso_camion = st.sidebar.slider("Peso del Camión (Toneladas):", min_value=1.0, max_value=40.0, value=15.0, step=0.5)

# Al hacer clic, guardamos los datos en la memoria de la sesión
if st.sidebar.button("Calcular Ruta Óptima", type="primary"):
    with st.spinner('Consultando el grafo en Neo4j...'):
        ruta = obtener_ruta_optima(origen, destino, peso_camion)
        st.session_state.datos_ruta = ruta
        st.session_state.ruta_calculada = True

# --- MOSTRAR RESULTADOS DESDE LA MEMORIA ---
if st.session_state.ruta_calculada:
    ruta = st.session_state.datos_ruta
    
    if ruta:
        # --- MÉTRICAS (KPIs) ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Distancia Total", f"{ruta['distancia_total']:.2f} km")
        col2.metric("Costo Dinámico (con Tráfico)", f"{ruta['costo_total']:.2f} pts")
        col3.metric("Nodos Recorridos", len(ruta['coordenadas']))
        
        # --- MAPA GEOESPACIAL (Folium) ---
        st.subheader("Visualización de la Ruta")
        
        # Centrar el mapa en el origen
        coord_origen = [ruta['coordenadas'][0]['lat'], ruta['coordenadas'][0]['lon']]
        m = folium.Map(location=coord_origen, zoom_start=13)
        
        puntos_ruta = []
        for parada in ruta['coordenadas']:
            puntos_ruta.append([parada['lat'], parada['lon']])
            
            # Diferenciar colores por tipo de nodo
            color = "green" if parada['tipo'] == "Almacén" else "red" if parada['tipo'] == "PuntoEntrega" else "blue"
            icono = "home" if parada['tipo'] == "Almacén" else "flag" if parada['tipo'] == "PuntoEntrega" else "info-sign"
            
            folium.Marker(
                location=[parada['lat'], parada['lon']],
                popup=f"{parada['tipo']}: {parada['id']}",
                icon=folium.Icon(color=color, icon=icono)
            ).add_to(m)
        
        # Dibujar la línea de la ruta
        folium.PolyLine(puntos_ruta, color="red", weight=4, opacity=0.8).add_to(m)
        
        # Mostrar mapa en Streamlit (returned_objects=[] evita el parpadeo al interactuar con el mapa)
        st_folium(m, width=1000, height=500, returned_objects=[])
        
    else:
        st.warning(f"⚠️ No existe una ruta viable para un camión de {peso_camion} toneladas entre {origen} y {destino}.")