MATCH (n) DETACH DELETE n;

CREATE CONSTRAINT intersection_id_unique IF NOT EXISTS
FOR (i:Intersección) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT almacen_id_unique IF NOT EXISTS
FOR (a:Almacén) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT entrega_id_unique IF NOT EXISTS
FOR (p:PuntoEntrega) REQUIRE p.id IS UNIQUE;

CREATE INDEX ubicacion_nombre_idx IF NOT EXISTS
FOR (n:Intersección) ON (n.nombre);

CREATE (:Almacén {id:'A-01', latitud:8.2953, longitud:-62.7111});
CREATE (:Almacén {id:'A-02', latitud:8.3000, longitud:-62.7000});

CREATE (:Intersección {id:'I-01', latitud:8.2960, longitud:-62.7100});
CREATE (:Intersección {id:'I-02', latitud:8.2975, longitud:-62.7080});
CREATE (:Intersección {id:'I-03', latitud:8.2980, longitud:-62.7050});
CREATE (:Intersección {id:'I-04', latitud:8.2990, longitud:-62.7020});
CREATE (:Intersección {id:'I-05', latitud:8.3000, longitud:-62.7060});

CREATE (:PuntoEntrega {id:'P-01', latitud:8.2985, longitud:-62.7010});
CREATE (:PuntoEntrega {id:'P-02', latitud:8.2995, longitud:-62.6990});

MATCH (a:Almacén{id:'A-01'}),(i1:Intersección{id:'I-01'})
CREATE (a)-[:CONECTA_A{
distancia:2.5,
tiempo_estimado:5,
estado_trafico:0.1,
capacidad_max_toneladas:40
}]->(i1);

MATCH (i1:Intersección{id:'I-01'}),(i2:Intersección{id:'I-02'})
CREATE (i1)-[:CONECTA_A{
distancia:3,
tiempo_estimado:7,
estado_trafico:0.5,
capacidad_max_toneladas:40
}]->(i2);

MATCH (i2:Intersección{id:'I-02'}),(i3:Intersección{id:'I-03'})
CREATE (i2)-[:CONECTA_A{
distancia:1.5,
tiempo_estimado:15,
estado_trafico:0.9,
capacidad_max_toneladas:12
}]->(i3);

MATCH (i3:Intersección{id:'I-03'}),(p:PuntoEntrega{id:'P-01'})
CREATE (i3)-[:CONECTA_A{
distancia:2,
tiempo_estimado:4,
estado_trafico:0.2,
capacidad_max_toneladas:40
}]->(p);

MATCH (i2:Intersección{id:'I-02'}),(i4:Intersección{id:'I-04'})
CREATE (i2)-[:CONECTA_A{
distancia:6,
tiempo_estimado:10,
estado_trafico:0.1,
capacidad_max_toneladas:40
}]->(i4);

MATCH (i4:Intersección{id:'I-04'}),(p:PuntoEntrega{id:'P-01'})
CREATE (i4)-[:CONECTA_A{
distancia:3.5,
tiempo_estimado:6,
estado_trafico:0.2,
capacidad_max_toneladas:40
}]->(p);

MATCH (i2:Intersección{id:'I-02'}),(i5:Intersección{id:'I-05'})
CREATE (i2)-[:CONECTA_A{
distancia:4,
tiempo_estimado:8,
estado_trafico:0.7,
capacidad_max_toneladas:40
}]->(i5);

MATCH (i5:Intersección{id:'I-05'}),(p:PuntoEntrega{id:'P-01'})
CREATE (i5)-[:CONECTA_A{
distancia:2,
tiempo_estimado:5,
estado_trafico:0.1,
capacidad_max_toneladas:40
}]->(p);
