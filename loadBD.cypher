// 1. Limpieza total de la base de datos para asegurar carga limpia
MATCH (n) DETACH DELETE n;

// 2. Creación de Nodos según el modelo sugerido [cite: 9]
CREATE (a:Almacen {id: 'ALM-01', nombre: 'Depósito Central', capacidad_max: 50.0})
CREATE (p1:PuntoEntrega {id: 'P-101', nombre: 'Tienda Norte'})
CREATE (p2:PuntoEntrega {id: 'P-102', nombre: 'Tienda Sur'})
CREATE (i1:Interseccion {id: 'INT-01', nombre: 'Cruce Principal'})

// 3. Creación de Relaciones CONECTA_A con propiedades obligatorias [cite: 9]
// Nota: estado_trafico (0.0 a 1.0) se usará para el costo de ruta [cite: 14]
CREATE (a)-[:CONECTA_A {distancia: 12.5, tiempo_estimado: 20, estado_trafico: 0.8, limite_carga: 20.0}]->(i1)
CREATE (i1)-[:CONECTA_A {distancia: 5.0, tiempo_estimado: 10, estado_trafico: 0.3, limite_carga: 40.0}]->(p1)
CREATE (i1)-[:CONECTA_A {distancia: 15.2, tiempo_estimado: 25, estado_trafico: 0.5, limite_carga: 10.0}]->(p2);