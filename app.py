# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from services.routing import (
    obtener_ruta_optima, 
    obtener_ruta_optima_astar, 
    obtener_nodos_por_tipo,
    crear_proyeccion
)
from database.seed import seed_if_empty
seed_if_empty()


def asegurar_proyeccion(origen_id, destino_id, peso_camion):
    """
    Reproyecta SOLO si:
    - Nunca se proyectó
    - El peso cambió
    """

    if (
        not st.session_state.grafo_proyectado
        or st.session_state.peso_proyectado != peso_camion
    ):

        crear_proyeccion(origen_id, destino_id, peso_camion)

        st.session_state.grafo_proyectado = True
        st.session_state.peso_proyectado = peso_camion



# Configuración de la página
st.set_page_config(page_title="Logistics Optimizer", layout="wide")
st.title("🚚 Proyecto III: Smart Routing Optimizer")
st.markdown("Sistema de enrutamiento logístico basado en **Neo4j** y **Graph Data Science**.")

# --- INICIALIZAR LA MEMORIA DE LA SESIÓN ---
if 'ruta_calculada' not in st.session_state:
    st.session_state.ruta_calculada = False
if 'datos_ruta' not in st.session_state:
    st.session_state.datos_ruta = None

if 'algoritmo' not in st.session_state:
    st.session_state.algoritmo = None

if 'ruta_d' not in st.session_state:
    st.session_state.ruta_d = None

if 'ruta_a' not in st.session_state:
    st.session_state.ruta_a = None

# --- ESTADO GLOBAL DE PROYECCIÓN ---
if "peso_proyectado" not in st.session_state:
    st.session_state.peso_proyectado = None

if "grafo_proyectado" not in st.session_state:
    st.session_state.grafo_proyectado = False

if "ruta_calculada" not in st.session_state:
    st.session_state.ruta_calculada = False

# --- BARRA LATERAL ---
st.sidebar.header("Configuración de la Ruta")

try:
    almacenes = obtener_nodos_por_tipo("Almacén")
    puntos = obtener_nodos_por_tipo("PuntoEntrega")
except Exception:
    st.error("Error conectando a Neo4j. Verifica tus credenciales en el archivo .env.")
    st.stop()

origen = st.sidebar.selectbox("Seleccione Almacén de Origen:", almacenes)
destino = st.sidebar.selectbox("Seleccione Punto de Destino:", puntos)

peso_camion = st.sidebar.slider(
    "Peso del Camión (Toneladas):",
    min_value=1.0,
    max_value=40.0,
    value=15.0,
    step=0.5
)


# --- BOTONES ---

if st.sidebar.button("Calcular Ruta con Dijkstra"):

    asegurar_proyeccion(origen, destino, peso_camion)

    with st.spinner("Ejecutando Dijkstra..."):
        st.session_state.datos_ruta = obtener_ruta_optima(origen, destino, peso_camion)
        st.session_state.algoritmo = "dijkstra"
        st.session_state.ruta_calculada = True


if st.sidebar.button("Calcular Ruta con A*"):

    asegurar_proyeccion(origen, destino, peso_camion)

    with st.spinner("Ejecutando A*..."):
        st.session_state.datos_ruta = obtener_ruta_optima_astar(origen, destino, peso_camion)
        st.session_state.algoritmo = "astar"
        st.session_state.ruta_calculada = True


if st.sidebar.button("Comparar Dijkstra vs A*"):

    asegurar_proyeccion(origen, destino, peso_camion)

    with st.spinner("Comparando algoritmos..."):
        st.session_state.ruta_d = obtener_ruta_optima(origen, destino, peso_camion)
        st.session_state.ruta_a = obtener_ruta_optima_astar(origen, destino, peso_camion)
        st.session_state.algoritmo = "comparar"
        st.session_state.ruta_calculada = True


# --- RESULTADO DE UN SOLO ALGORITMO ---

if st.session_state.ruta_calculada and st.session_state.algoritmo != "comparar":

    ruta = st.session_state.datos_ruta
    
    if ruta:

        col1, col2, col3 = st.columns(3)

        if st.session_state.algoritmo == "dijkstra":

            col1.metric("Distancia Total", f"{ruta['distancia_total']:.2f} km")
            col2.metric("Peso Distancia", f"{ruta['costo_total']:.2f}")
            col3.metric("Nodos Recorridos", len(ruta['coordenadas']))
            color_ruta = "blue"

        else:

            col1.metric("Tiempo Total con Tráfico", f"{ruta['tiempo_total']:.2f}")
            col2.metric("Peso Tiempo/Tráfico", f"{ruta['tiempo_total']:.2f}")
            col3.metric("Nodos Recorridos", len(ruta['coordenadas']))
            color_ruta = "red"

        st.subheader("Visualización de la Ruta")

        coord_origen = [
            ruta['coordenadas'][0]['lat'],
            ruta['coordenadas'][0]['lon']
        ]

        m = folium.Map(location=coord_origen, zoom_start=13)

        puntos_ruta = []

        for parada in ruta['coordenadas']:

            puntos_ruta.append([parada['lat'], parada['lon']])

            color = "green" if parada['tipo'] == "Almacén" else "red" if parada['tipo'] == "PuntoEntrega" else "blue"
            icono = "home" if parada['tipo'] == "Almacén" else "flag" if parada['tipo'] == "PuntoEntrega" else "info-sign"

            folium.Marker(
                location=[parada['lat'], parada['lon']],
                popup=f"{parada['tipo']}: {parada['id']}",
                icon=folium.Icon(color=color, icon=icono)
            ).add_to(m)

        folium.PolyLine(
            puntos_ruta,
            color=color_ruta,
            weight=4,
            opacity=0.8
        ).add_to(m)

        st_folium(m, width=1000, height=500, returned_objects=[])

    else:
        st.warning(
            f"⚠️ No existe una ruta viable para un camión de {peso_camion} toneladas entre {origen} y {destino}."
        )


# --- COMPARACIÓN DE ALGORITMOS ---

if st.session_state.algoritmo == "comparar":

    ruta_d = st.session_state.ruta_d
    ruta_a = st.session_state.ruta_a

    if ruta_d and ruta_a:

        col1, col2 = st.columns(2)

        col1.metric(
            "Distancia Ruta Dijkstra",
            f"{ruta_d['distancia_total']:.2f} km"
        )

        col2.metric(
            "Tiempo Ruta A* (tráfico)",
            f"{ruta_a['tiempo_total']:.2f}"
        )

        coord_origen = [
            ruta_d['coordenadas'][0]['lat'],
            ruta_d['coordenadas'][0]['lon']
        ]

        m = folium.Map(location=coord_origen, zoom_start=13)

        # --- DIJKSTRA (AZUL) ---
        puntos_d = [[p['lat'], p['lon']] for p in ruta_d['coordenadas']]
        folium.PolyLine(
            puntos_d,
            color="blue",
            weight=5,
            opacity=0.9
        ).add_to(m)

        # --- A* (ROJO)--
        puntos_a = []
        for p in ruta_a['coordenadas']:
            puntos_a.append([
                p['lat'] + 0.00015,   # pequeño offset visual
                p['lon'] + 0.00015
            ])

        folium.PolyLine(
            puntos_a,
            color="red",
            weight=5,
            opacity=0.9
        ).add_to(m)

        # --- LEYENDA CORREGIDA ---
        legend_html = """
        <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        width: 170px;
        background-color: white;
        border:2px solid grey;
        z-index:9999;
        font-size:14px;
        color:black;
        padding:10px;
        ">
        <b>Leyenda</b><br>
        <span style="color:blue;">████</span> Dijkstra<br>
        <span style="color:red;">████</span> A*
        </div>
        """

        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, width=1000, height=500, returned_objects=[])