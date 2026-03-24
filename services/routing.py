from database.connection import Neo4jConnection

"""
Función modificada para el uso explícito de gds.shortestPath.dijkstra
con el peso "distancia"
"""
def obtener_ruta_optima(origen_id, destino_id, peso_camion):

    conn = Neo4jConnection()

    query = """
    MATCH (o:Almacén {id:$origen_id})
    MATCH (d:PuntoEntrega {id:$destino_id})

    CALL gds.shortestPath.dijkstra.stream(
        'routingGraph',
        {
            sourceNode:o,
            targetNode:d,
            relationshipWeightProperty:'distancia'
        }
    )
    YIELD totalCost,nodeIds

    WITH totalCost,nodeIds,
         [nodeId IN nodeIds | gds.util.asNode(nodeId)] AS nodes

    RETURN totalCost AS distancia_total,
           totalCost AS costo_total,
           [n IN nodes |
                {id:n.id,lat:n.latitud,lon:n.longitud,tipo:labels(n)[0]}
           ] AS coordenadas
    """

    params = {
        "origen_id": origen_id,
        "destino_id": destino_id
    }

    resultado = conn.execute_read_query(query, params)

    conn.close()

    return resultado[0] if resultado else None


# Obtener ruta optima con el algoritmo A*, donde el peso es tiempo
def obtener_ruta_optima_astar(origen_id, destino_id, peso_camion):

    conn = Neo4jConnection()
    query = """
    MATCH (o:Almacén {id:$origen_id})
    MATCH (d:PuntoEntrega {id:$destino_id})

    CALL gds.shortestPath.astar.stream('routingGraph', {
            sourceNode: o,
            targetNode: d,
            latitudeProperty: 'latitud',
            longitudeProperty: 'longitud',
            relationshipWeightProperty:'tiempo_trafico'
    })
    YIELD totalCost,nodeIds

    WITH totalCost,nodeIds,
         [nodeId IN nodeIds | gds.util.asNode(nodeId)] AS nodes

    RETURN totalCost AS tiempo_total,
           [n IN nodes |
                {id:n.id,lat:n.latitud,lon:n.longitud,tipo:labels(n)[0]}
           ] AS coordenadas
    """

    params = {
        "origen_id": origen_id,
        "destino_id": destino_id
    }

    resultado = conn.execute_read_query(query, params)

    conn.close()

    return resultado[0] if resultado else None


def obtener_nodos_por_tipo(tipo_nodo):
    """Obtiene la lista de IDs para los selectores del dashboard."""
    conn = Neo4jConnection()
    query = f"MATCH (n:{tipo_nodo}) RETURN n.id AS id ORDER BY n.id"
    resultado = conn.execute_read_query(query)
    conn.close()
    return [record["id"] for record in resultado]


def crear_proyeccion(origen_id, destino_id, peso_camion):

    conn = Neo4jConnection()
    """
    Elimina proyección previa si existe, 
    debido a que el peso del camión puede cambiar
    y afectar las rutas
    """
    conn.execute_write_query("""
        CALL gds.graph.drop('routingGraph', false)
        YIELD graphName
    """)

    projection_query = """
    CALL () {
        WITH $peso_camion AS peso_camion

        MATCH (source)
        WHERE source:Almacén OR source:PuntoEntrega OR source:Intersección

        OPTIONAL MATCH (source)-[r:CONECTA_A]->(target)
        WHERE r.capacidad_max_toneladas >= peso_camion

        RETURN gds.graph.project(
            'routingGraph',
            source,
            target,
            {
                sourceNodeProperties: source {
                    .latitud,
                    .longitud
                },
                targetNodeProperties: target {
                    .latitud,
                    .longitud
                },
                relationshipProperties: {
                    distancia: r.distancia,
                    tiempo_trafico: r.tiempo_estimado * (1 + r.estado_trafico)
                }
            }
        ) AS graphInfo
    }

    RETURN graphInfo
    """

    params = {
        "origen_id": origen_id,
        "destino_id": destino_id,
        "peso_camion": peso_camion
    }

    conn.execute_write_query(projection_query, params)

    conn.close()
