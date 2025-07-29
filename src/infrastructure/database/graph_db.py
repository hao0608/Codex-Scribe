"""
This module provides a service for interacting with a Neo4j graph database.
"""

from neo4j import GraphDatabase, Transaction

from src.domain.entities.graph_entities import BaseEdge, BaseNode


class Neo4jService:
    """
    A service to manage connections and operations with a Neo4j database.
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        """
        Initializes the Neo4jService and connects to the database.
        """
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        """Closes the database connection."""
        self._driver.close()

    def add_node(self, node: BaseNode) -> None:
        """
        Adds a node to the graph.
        It uses MERGE to avoid creating duplicate nodes.
        """
        with self._driver.session() as session:
            session.write_transaction(self._create_node_tx, node)

    def add_edge(self, edge: BaseEdge) -> None:
        """
        Adds an edge between two existing nodes.
        """
        with self._driver.session() as session:
            session.write_transaction(self._create_edge_tx, edge)

    def clear_database(self) -> None:
        """
        Deletes all nodes and relationships from the database.
        USE WITH CAUTION.
        """
        with self._driver.session() as session:
            session.write_transaction(self._clear_db_tx)

    @staticmethod
    def _create_node_tx(tx: Transaction, node: BaseNode) -> None:
        """Transaction function to create a single node."""
        query = f"MERGE (n:{node.type.value} {{id: $id}}) " "SET n += $properties"
        tx.run(query, id=node.id, properties=node.properties)

    @staticmethod
    def _create_edge_tx(tx: Transaction, edge: BaseEdge) -> None:
        """Transaction function to create a single edge."""
        query = (
            f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
            f"MERGE (a)-[r:{edge.type.value}]->(b) "
            "SET r += $properties"
        )
        tx.run(
            query,
            source_id=edge.source_id,
            target_id=edge.target_id,
            properties=edge.properties,
        )

    @staticmethod
    def _clear_db_tx(tx: Transaction) -> None:
        """Transaction function to clear the database."""
        tx.run("MATCH (n) DETACH DELETE n")
