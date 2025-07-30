"""
This module contains the use case for querying the knowledge graph.
"""

from typing import Any

from neo4j import Driver


class GraphQueryUseCase:
    """
    Use case for running queries against the Neo4j knowledge graph.
    """

    def __init__(self, driver: Driver):
        """
        Initializes the GraphQueryUseCase.
        """
        self._driver = driver

    def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Executes a raw Cypher query and returns the results.
        """
        with self._driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]

    def get_function_callers(self, function_name: str) -> list[dict[str, Any]]:
        """
        Finds all functions that call a specific function.
        """
        query = """
        MATCH (caller)-[:CALLS]->(callee:Function)
        WHERE callee.name = $function_name
        RETURN caller.id as caller_id, caller.name as caller_name
        """
        return self.execute_query(query, {"function_name": function_name})

    def get_class_dependencies(self, class_name: str) -> list[dict[str, Any]]:
        """
        Finds all modules that import a specific class.
        """
        query = """
        MATCH (importer)-[:IMPORTS]->(c:Class)
        WHERE c.name = $class_name
        RETURN importer.id as importer_id
        """
        return self.execute_query(query, {"class_name": class_name})

    def get_methods_in_class(self, class_name: str) -> list[dict[str, Any]]:
        """
        Finds all methods contained within a specific class.
        """
        query = """
        MATCH (c:Class)-[:CONTAINS]->(m:Function)
        WHERE c.name = $class_name
        RETURN m.id as method_id, m.name as method_name
        """
        return self.execute_query(query, {"class_name": class_name})
