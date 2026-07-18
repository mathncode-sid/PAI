import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load credentials .env file
load_dotenv()

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

        try:
            # Create the driver instance
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
            # Verify immediately that the driver can connect to the database
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j AuraDB!")
        except Exception as e:
            print(f"Failed to create the driver: {e}")

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def execute_query(self, query, **kwargs):
        """
        Executes a query using the modern driver.execute_query method.
        """
        records, summary, keys = self.driver.execute_query(
            query,
            database_="neo4j",
            **kwargs
        )
        return records

# Instantiate a single global connection object to be imported by the FastAPI routes
db = Neo4jConnection()