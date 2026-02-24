# database/seed.py
import sys
import os

# Añadir el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import Neo4jConnection


def inicializar_base_de_datos():
    conn = Neo4jConnection()

    print("🧹 1. Limpiando la base de datos...")
    conn.execute_write_query("MATCH (n) DETACH DELETE n")

    print("🏗️ 2. Creando Restricciones (Constraints) e Índices...")
    # Usamos IF NOT EXISTS para evitar errores si ya están creados
    restricciones = [
        "CREATE CONSTRAINT unique_almacen_id IF NOT EXISTS FOR (a:Almacén) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT unique_punto_id IF NOT EXISTS FOR (p:PuntoEntrega) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT unique_interseccion_id IF NOT EXISTS FOR (i:Intersección) REQUIRE i.id IS UNIQUE",
    ]
    for res in restricciones:
        conn.execute_write_query(res)

    print("📍 3. Insertando Nodos (Almacenes, Intersecciones, Puntos de Entrega)...")

    # Datos de los nodos
    query_nodos = """
    // Crear Almacenes
    CREATE (:Almacén {id: 'A-01', latitud: 8.2953, longitud: -62.7111, ciudad: 'Puerto Ordaz'}),
           (:Almacén {id: 'A-02', latitud: 8.3000, longitud: -62.7000, ciudad: 'San Félix'})
           
    // Crear Intersecciones
    CREATE (:Intersección {id: 'I-01', latitud: 8.2960, longitud: -62.7100}),
           (:Intersección {id: 'I-02', latitud: 8.2975, longitud: -62.7080}),
           (:Intersección {id: 'I-03', latitud: 8.2980, longitud: -62.7050}),
           (:Intersección {id: 'I-04', latitud: 8.2990, longitud: -62.7020})
           
    // Crear Puntos de Entrega
    CREATE (:PuntoEntrega {id: 'P-01', latitud: 8.2985, longitud: -62.7010, zona: 'Alta Vista'}),
           (:PuntoEntrega {id: 'P-02', latitud: 8.2995, longitud: -62.6990, zona: 'Unare'})
    """
    conn.execute_write_query(query_nodos)

    print("🔗 4. Creando Relaciones (CONECTA_A) con pesos y restricciones de carga...")

    # Datos de las relaciones (Rutas)
    # Nota: I-02 a I-03 simula un puente viejo que solo soporta 12 toneladas.
    # I-02 a I-04 es una ruta alternativa más larga pero soporta 40 toneladas.
    rutas = [
        {
            "origen": "A-01",
            "destino": "I-01",
            "dist": 2.5,
            "tiempo": 5,
            "trafico": 0.1,
            "capacidad": 40.0,
        },
        {
            "origen": "I-01",
            "destino": "I-02",
            "dist": 3.0,
            "tiempo": 7,
            "trafico": 0.5,
            "capacidad": 40.0,
        },
        # Ruta directa pero con restricción de peso (Ej: Puente de 12 Toneladas) y mucho tráfico
        {
            "origen": "I-02",
            "destino": "I-03",
            "dist": 1.5,
            "tiempo": 15,
            "trafico": 0.9,
            "capacidad": 12.0,
        },
        {
            "origen": "I-03",
            "destino": "P-01",
            "dist": 2.0,
            "tiempo": 4,
            "trafico": 0.2,
            "capacidad": 40.0,
        },
        # Ruta alternativa (Más larga, pero soporta gandolas de 40 Toneladas y tiene menos tráfico)
        {
            "origen": "I-02",
            "destino": "I-04",
            "dist": 6.0,
            "tiempo": 10,
            "trafico": 0.1,
            "capacidad": 40.0,
        },
        {
            "origen": "I-04",
            "destino": "P-01",
            "dist": 3.5,
            "tiempo": 6,
            "trafico": 0.2,
            "capacidad": 40.0,
        },
        # Conexiones hacia el segundo punto de entrega y segundo almacén
        {
            "origen": "P-01",
            "destino": "P-02",
            "dist": 4.0,
            "tiempo": 8,
            "trafico": 0.3,
            "capacidad": 20.0,
        },
        {
            "origen": "A-02",
            "destino": "I-04",
            "dist": 5.0,
            "tiempo": 9,
            "trafico": 0.4,
            "capacidad": 40.0,
        },
        {
            "origen": "A-02",
            "destino": "P-02",
            "dist": 2.2,
            "tiempo": 5,
            "trafico": 0.1,
            "capacidad": 40.0,
        },
    ]

    query_relaciones = """
    UNWIND $rutas AS ruta
    MATCH (origen {id: ruta.origen})
    MATCH (destino {id: ruta.destino})
    CREATE (origen)-[:CONECTA_A {
        distancia: ruta.dist,
        tiempo_estimado: ruta.tiempo,
        estado_trafico: ruta.trafico,
        capacidad_max_toneladas: ruta.capacidad
    }]->(destino)
    """

    conn.execute_write_query(query_relaciones, {"rutas": rutas})

    print("✅ ¡Base de datos inicializada con éxito!")
    conn.close()


if __name__ == "__main__":
    inicializar_base_de_datos()
