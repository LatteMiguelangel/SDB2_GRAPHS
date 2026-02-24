# 🚚 Proyecto III: Logistics Optimizer (Smart Routing)

**Universidad Nacional Experimental de Guayana (UNEG)**  
**Asignatura:** Sistemas de Bases de Datos II (Semestre 2025-II)  

Este proyecto es un sistema avanzado de enrutamiento logístico basado en bases de datos orientadas a grafos (**Neo4j**). Utiliza algoritmos de **Graph Data Science (GDS)** para calcular rutas óptimas evaluando variables en tiempo real como: distancia, estado del tráfico y la capacidad máxima de carga (toneladas) de las vías. Todo esto visualizado en un dashboard interactivo construido con **Streamlit** y **Folium**.

---

## 🛠️ Tecnologías Utilizadas
* **Base de Datos:** Neo4j Desktop (Cypher, APOC, GDS Library)
* **Backend:** Python 3.10+ (Driver oficial `neo4j`)
* **Frontend:** Streamlit
* **Mapas Geoespaciales:** Folium / Streamlit-Folium

---

## 📋 Requisitos Previos (Prerrequisitos)

Para que este proyecto funcione en tu máquina local, necesitas tener instalado lo siguiente:

1. **Python 3.9 o superior:** [Descargar aquí](https://www.python.org/downloads/) (Asegúrate de marcar la casilla "Add Python to PATH" durante la instalación).
2. **Neo4j Desktop:** [Descargar aquí](https://neo4j.com/download/). Es el motor de base de datos que ejecutará el grafo localmente.

---

## 🚀 Guía de Instalación Paso a Paso

Sigue estas instrucciones al pie de la letra para levantar el entorno en tu máquina.

### Fase 1: Configuración de la Base de Datos (Neo4j Desktop)

1. Instala y abre **Neo4j Desktop**.
2. Haz clic en el botón **"Create instance"** (o "Add" -> "Local DBMS").
3. Asigna un nombre a la instancia (ej. `LogisticsDB`) y establece una contraseña segura (ej. `admin1234`). **Anótala, la necesitarás más adelante**.
4. Selecciona la versión más reciente de Neo4j (ej. 5.x).
5. **¡IMPORTANTE! Instalar Plugins:**
   * Haz clic en tu nueva instancia.
   * En el panel derecho, ve a la pestaña **"Plugins"**.
   * Instala **APOC** y **Graph Data Science Library**.
6. Haz clic en el botón **"Start"** para iniciar el servidor de la base de datos. Espera a que el estado cambie a *Active/Running*.

### Fase 2: Clonar y Configurar el Entorno de Python

1. Abre una terminal (Símbolo del sistema, PowerShell o la terminal de VS Code) y ubícate en la carpeta donde deseas guardar el proyecto.
2. Clona este repositorio (o descomprime los archivos del proyecto).
3. Entra a la carpeta del proyecto:
   ```bash
   cd logistics_optimizer
   ```

4. Crea un entorno virtual para aislar las dependencias:
    ```bash
    python -m venv .venv
    ```

    Activa el entorno virtual:
        Windows: .venv\Scripts\activate
        Mac/Linux: source .venv/bin/activate

    Instala las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```

### Fase 3: Variables de Entorno

1. En la raíz del proyecto, crea un archivo llamado exactamente .env.
2. Abre el archivo y pega las credenciales de tu base de datos Neo4j (usa la contraseña que creaste en la Fase 1):
    
    ```bash
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=tu_contraseña_aqui
    ```

### Fase 4: Poblar la Base de Datos (Seeding)

1. Antes de usar el sistema, debemos crear los nodos (Almacenes, Puntos de Entrega, Intersecciones) y las relaciones (Vías) en Neo4j.
2. Asegúrate de que tu instancia de Neo4j Desktop esté en estado "Running".
En tu terminal (con el .venv activo), ejecuta:
```bash
python database/seed.py
```
3. Verás mensajes en la consola indicando que la base de datos se ha limpiado y que los datos de prueba se han insertado correctamente.

### Fase 5: Ejecutar el Dashboard Interactivo
En la misma terminal, levanta la interfaz gráfica ejecutando:
```bash
streamlit run app.py
```
Se abrirá automáticamente una pestaña en tu navegador web en la dirección http://localhost:8501.