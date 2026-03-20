from database.connection import Neo4jConnection
import os

def ejecutar_seed_cypher():

    conn = Neo4jConnection()

    path = os.path.join(os.path.dirname(__file__), "db.cypher")

    with open(path, "r", encoding="utf-8") as file:
        cypher_script = file.read()

    for query in cypher_script.split(";"):
        q = query.strip()
        if q:
            conn.execute_write_query(q)

    conn.close()
    print("Base de datos cargada desde db.cypher")

def seed_if_empty():

    conn = Neo4jConnection()

    result = conn.execute_read_query("MATCH (n) RETURN count(n) as total")

    if result[0]["total"] == 0:
        ejecutar_seed_cypher()

    conn.close()  