from database.connection import Neo4jConnection

def obtener_ruta_optima(origen_id, destino_id, peso_camion):
    """
    Calcula la ruta óptima verificando que los puentes/vías soporten el peso del camión.
    """
    conn = Neo4jConnection()
    
    query = """
    MATCH (origen:Almacén {id: $origen_id})
    MATCH (destino:PuntoEntrega {id: $destino_id})
    // Buscar rutas de hasta 10 saltos
    MATCH ruta = (origen)-[rels:CONECTA_A*1..10]->(destino)
    // Filtrado en tiempo real: todas las vías deben soportar el peso
    WHERE ALL(r IN rels WHERE r.capacidad_max_toneladas >= $peso_camion)
    // Calcular costo dinámico (distancia penalizada por tráfico)
    WITH ruta, nodes(ruta) AS paradas,
         reduce(costo = 0, r IN rels | costo + (r.distancia * (1 + r.estado_trafico))) AS costo_total,
         reduce(dist = 0, r IN rels | dist + r.distancia) AS distancia_total
    ORDER BY costo_total ASC
    LIMIT 1
    
    // Extraer coordenadas para el mapa
    RETURN costo_total, distancia_total,
           [n IN paradas | {id: n.id, lat: n.latitud, lon: n.longitud, tipo: labels(n)[0]}] AS coordenadas
    """
    
    parametros = {
        "origen_id": origen_id,
        "destino_id": destino_id,
        "peso_camion": float(peso_camion)
    }
    
    resultado = conn.execute_read_query(query, parametros)
    conn.close()
    
    return resultado[0] if resultado else None

def obtener_nodos_por_tipo(tipo_nodo):
    """Obtiene la lista de IDs para los selectores del dashboard."""
    conn = Neo4jConnection()
    query = f"MATCH (n:{tipo_nodo}) RETURN n.id AS id ORDER BY n.id"
    resultado = conn.execute_read_query(query)
    conn.close()
    return [record["id"] for record in resultado]