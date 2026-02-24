import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        pwd = os.getenv("NEO4J_PASSWORD")
        self.__driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def execute_read_query(self, query, parameters=None):
        with self.__driver.session() as session:
            # Actualizado para el driver Neo4j 5.x: usamos execute_read
            result = session.execute_read(lambda tx: tx.run(query, parameters).data())
            return result

    def execute_write_query(self, query, parameters=None):
        with self.__driver.session() as session:
            # Actualizado para el driver Neo4j 5.x: usamos execute_write
            session.execute_write(lambda tx: tx.run(query, parameters))