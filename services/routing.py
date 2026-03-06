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
            sourceNode:id(o),
            targetNode:id(d),
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

    CALL gds.shortestPath.astar.stream(
        'routingGraph',
        {
            sourceNode:id(o),
            targetNode:id(d),
            latitudeProperty:'lat',
            longitudeProperty:'lon',
            relationshipWeightProperty:'tiempo_trafico'
        }
    )
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

    # Elimina proyección previa si existe
    conn.execute_write_query("""
        CALL gds.graph.drop('routingGraph', false)
        YIELD graphName
    """)

    projection_query = """
    CALL gds.graph.project.cypher(
        'routingGraph',

        'MATCH (n)
         WHERE n:Almacén OR n:PuntoEntrega OR n:Intersección
         RETURN id(n) AS id,
                n.latitud AS lat,
                n.longitud AS lon',

        '
        MATCH (n)-[r:CONECTA_A]->(m)
        WHERE r.capacidad_max_toneladas >= $peso_camion
        RETURN id(n) AS source,
               id(m) AS target,
               r.distancia AS distancia,
               r.tiempo_estimado * (1 + r.estado_trafico) AS tiempo_trafico
        ',

        {parameters:{peso_camion:$peso_camion}}
    )
    YIELD graphName
    """

    conn.execute_write_query(
        projection_query,
        {"peso_camion": float(peso_camion)}
    )

    conn.close()
