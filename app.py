# app.py
import pandas as pd
import time
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


# Función para detectar si ambos algoritmos generaron la misma ruta
def rutas_identicas(r1, r2):
    coords1 = [(p['lat'], p['lon']) for p in r1['coordenadas']]
    coords2 = [(p['lat'], p['lon']) for p in r2['coordenadas']]
    return coords1 == coords2

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
        t_beginning = time.perf_counter()
        st.session_state.datos_ruta = obtener_ruta_optima(origen, destino, peso_camion)
        t_end = time.perf_counter()
        st.session_state.algoritmo = "dijkstra"
        st.session_state.ruta_calculada = True
        t_latency = (t_end - t_beginning) * 1000
        st.session_state.ms_ejecucion = t_latency


if st.sidebar.button("Calcular Ruta con A*"):

    asegurar_proyeccion(origen, destino, peso_camion)

    with st.spinner("Ejecutando A*..."):
        t_beginning = time.perf_counter()
        st.session_state.datos_ruta = obtener_ruta_optima_astar(origen, destino, peso_camion)
        t_end = time.perf_counter()
        st.session_state.algoritmo = "astar"
        st.session_state.ruta_calculada = True
        t_latency = (t_end - t_beginning) * 1000
        st.session_state.ms_ejecucion = t_latency



if st.sidebar.button("Comparar Dijkstra vs A*"):

    asegurar_proyeccion(origen, destino, peso_camion)

    with st.spinner("Comparando algoritmos..."):

        t_beginning_dijks = time.perf_counter()
        st.session_state.ruta_d = obtener_ruta_optima(origen, destino, peso_camion)
        t_end_dijks = time.perf_counter()
        st.session_state.ms_dijkstra = (t_end_dijks - t_beginning_dijks) * 1000

        t_beginning_astar = time.perf_counter()
        st.session_state.ruta_a = obtener_ruta_optima_astar(origen, destino, peso_camion)
        t_end_astar = time.perf_counter()
        st.session_state.ms_astar = (t_end_astar - t_beginning_astar) * 1000

        st.session_state.algoritmo = "comparar"
        st.session_state.ruta_calculada = True


# --- RESULTADO DE UN SOLO ALGORITMO ---

if st.session_state.ruta_calculada and st.session_state.algoritmo != "comparar":

    ruta = st.session_state.datos_ruta
    tiempo = st.session_state
    if ruta:

        col1, col2, col3, col4 = st.columns(4)

        if st.session_state.algoritmo == "dijkstra":

            col1.metric("Distancia Total", f"{ruta['distancia_total']:.2f} km")
            col2.metric("Peso Distancia", f"{ruta['costo_total']:.2f} km")
            col3.metric("Nodos Recorridos", len(ruta['coordenadas']))
            col4.metric("Execution time ",f"{st.session_state.ms_ejecucion:.2f} ms" )
            color_ruta = "blue"

        else:

            col1.metric("Tiempo Total con Tráfico", f"{ruta['tiempo_total']:.2f} mins")
            col2.metric("Peso Tiempo/Tráfico", f"{ruta['tiempo_total']:.2f} mins")
            col3.metric("Nodos Recorridos", len(ruta['coordenadas']))
            col4.metric("Execution time ",f"{st.session_state.ms_ejecucion:.2f} ms" )
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

        with st.expander("🗺 ver detalles de la hoja de ruta "):

            st.info("note: Los IDs de los nodos corresponde a la base de datos neo4j")

            if st.session_state.algoritmo == "comparar":
                option = st.radio(
                "Selecciona que hoja de ruta quieres comprobar: ",
                ["dijkstra","A*","Ambos"],
                horizontal=True
                )
                if option == "dijkstra":
                    df_d = pd.DataFrame(st.session_state.ruta_d['coordenadas'])

                    columnas_visibles = ['lat', 'lon']
                    df_para_mostrar = df_d[columnas_visibles]

                    st.dataframe(df_para_mostrar, use_container_width=True)


                elif option == "A*":
                    df_a = pd.DataFrame(st.session_state.ruta_a['coordenadas'])

                    columnas_visibles = ['lat', 'lon']
                    df_para_mostrar = df_a[columnas_visibles]

                    st.dataframe(df_para_mostrar, use_container_width=True)

                else:
                    df_d = pd.DataFrame(st.session_state.ruta_d['coordenadas'])
                    columnas_visibles = ['lat', 'lon']
                    df_para_mostrar = df_d[columnas_visibles]
                    st.dataframe(df_para_mostrar, use_container_width=True)


                    df_a = pd.DataFrame(st.session_state.ruta_a['coordenadas'])
                    columnas_visibles = ['lat', 'lon']
                    df_para_mostrar = df_a[columnas_visibles]
                    st.dataframe(df_para_mostrar, use_container_width=True)

            else:
                st.write(F"Mostrando hoja de ruta para:**{st.session_state.algoritmo.upper()}**")

                df_unica = pd.DataFrame(st.session_state.datos_ruta['coordenadas'])


                columnas_visibles = ['lat', 'lon']
                df_para_mostrar = df_unica[columnas_visibles]

                st.dataframe(df_para_mostrar, use_container_width=True)


    else:
        st.warning(
            f"⚠️ No existe una ruta viable para un camión de {peso_camion} toneladas entre {origen} y {destino}."
        )


# --- COMPARACIÓN DE ALGORITMOS ---

if st.session_state.algoritmo == "comparar":

    ruta_d = st.session_state.ruta_d
    ruta_a = st.session_state.ruta_a

    if ruta_d and ruta_a:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Distancia Ruta Dijkstra",
            f"{ruta_d['distancia_total']:.2f} km"
        )

        col2.metric(
            "Tiempo de ejecución Dijkstra",
            f"{st.session_state.ms_dijkstra:.2f} ms"
        )

        col3.metric(
            "Tiempo Ruta A* (tráfico)",
            f"{ruta_a['tiempo_total']:.2f} mins"
        )

        col4.metric(
            "Tiempo de ejecución A*",
            f"{st.session_state.ms_astar:.2f} ms"
        )

        difference = abs(st.session_state.ms_dijkstra - st.session_state.ms_astar)
        if st.session_state.ms_astar < st.session_state.ms_dijkstra:
            st.success(f"🙌 A* fue {difference:.2f} ms más rápido que Dijkstra en esta búsqueda.")
        else:
            st.info(f"⚖ Dijkstra fue {difference:.2f} ms más rápido,pero A* optimizó el tráfico.")


        difference_mins = abs(ruta_d['tiempo_total'] - ruta_a['tiempo_total'])
        st.write(f"🤑la diferencia estimada de llegada entre ambas rutas es de **{difference_mins:.2f} minutos**.")

        # DETECTAR SI LAS RUTAS SON IDÉNTICAS
        son_iguales = rutas_identicas(ruta_d, ruta_a)

        coord_origen = [
            ruta_d['coordenadas'][0]['lat'],
            ruta_d['coordenadas'][0]['lon']
        ]

        m = folium.Map(location=coord_origen, zoom_start=13)

        # MARCADORES

        nodos = {}

        for p in ruta_d['coordenadas']:
            nodos[p['id']] = p

        for p in ruta_a['coordenadas']:
            nodos[p['id']] = p

        for parada in nodos.values():

            color = (
                "green" if parada['tipo'] == "Almacén"
                else "red" if parada['tipo'] == "PuntoEntrega"
                else "blue"
            )

            icono = (
                "home" if parada['tipo'] == "Almacén"
                else "flag" if parada['tipo'] == "PuntoEntrega"
                else "info-sign"
            )

            folium.Marker(
                location=[parada['lat'], parada['lon']],
                popup=f"{parada['tipo']}: {parada['id']}",
                icon=folium.Icon(color=color, icon=icono)
            ).add_to(m)

        # RENDERIZADO DE RUTAS

        if son_iguales:

            # Ruta unificada (resultado idéntico)
            puntos = [
                [p['lat'], p['lon']]
                for p in ruta_d['coordenadas']
            ]

            folium.PolyLine(
                puntos,
                color="purple",
                weight=6,
                opacity=0.9,
            ).add_to(m)

            legend_html = """
            <div style="
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 240px;
            background-color: white;
            border:2px solid grey;
            z-index:9999;
            font-size:14px;
            color:black;
            padding:10px;
            ">
            <b>Leyenda</b><br>
            <span style="color:purple;">████</span> Dijkstra & A* (Ruta idéntica)
            </div>
            """

        else:

            puntos_d = [
                [p['lat'], p['lon']]
                for p in ruta_d['coordenadas']
            ]

            folium.PolyLine(
                puntos_d,
                color="blue",
                weight=5,
                opacity=0.9
            ).add_to(m)

            puntos_a = [
                [p['lat'], p['lon']]
                for p in ruta_a['coordenadas']
            ]

            folium.PolyLine(
                puntos_a,
                color="red",
                weight=5,
                opacity=0.9,
                dash_array="8,4"
            ).add_to(m)

            legend_html = """
            <div style="
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 200px;
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

    else:
        st.warning(
            f"⚠️ No existe una ruta viable para un camión de {peso_camion} toneladas entre {origen} y {destino}."
        )