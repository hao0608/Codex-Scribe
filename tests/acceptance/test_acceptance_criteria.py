"""
Acceptance tests for Phase 3: Knowledge Graph.
"""

import subprocess
from unittest.mock import MagicMock

import pytest

from src.application.use_cases.answer_question import AnswerQuestionUseCase
from src.application.use_cases.graph_query import GraphQueryUseCase
from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.infrastructure.database.graph_db import Neo4jService
from src.infrastructure.llm.openai_client import OpenAIClient


@pytest.fixture
def real_neo4j_service() -> Neo4jService:
    """Fixture for a real Neo4jService connection."""
    # NOTE: Requires a running Neo4j instance
    service = Neo4jService("bolt://localhost:7687", "neo4j", "password123")
    yield service
    service.close()


def test_indexing_pipeline_creates_nodes_and_relationships(
    real_neo4j_service: Neo4jService,
) -> None:
    """
    Tests that the indexing pipeline correctly creates nodes and relationships.
    This is a placeholder and should be run after a real indexing process.
    """
    # Arrange
    # Run the indexing script first
    repo_path = "."  # Index the current project
    process = subprocess.run(
        ["python", "scripts/index_repository.py", repo_path],
        capture_output=True,
        text=True,
    )
    assert process.returncode == 0, f"Indexing script failed: {process.stderr}"

    use_case = GraphQueryUseCase(real_neo4j_service._driver)
    query = "MATCH (n) RETURN count(n) as count"

    # Act
    result = use_case.execute_query(query)

    # Assert
    # This will fail if the database is empty. Run the indexer first.
    assert len(result) > 0 and result[0]["count"] > 0


def test_cypher_query_finds_function_callers(
    real_neo4j_service: Neo4jService,
) -> None:
    """
    Tests a specific Cypher query to find function callers.
    This is a placeholder and depends on the indexed data.
    """
    # Arrange
    use_case = GraphQueryUseCase(real_neo4j_service._driver)

    # Act
    # Assuming 'parse' is a function in the indexed data
    callers = use_case.get_function_callers("parse")

    # Assert
    assert isinstance(callers, list)


def test_ai_agent_routes_to_graph_query() -> None:
    """
    Tests that the AI agent correctly routes to the graph query tool.
    """
    # Arrange
    mock_graph_query_use_case = MagicMock(spec=GraphQueryUseCase)
    use_case = AnswerQuestionUseCase(
        embedding_service=MagicMock(spec=EmbeddingService),
        code_repository=MagicMock(spec=CodeRepository),
        llm_client=MagicMock(spec=OpenAIClient),
        graph_query_use_case=mock_graph_query_use_case,
    )
    query = 'Who calls the "parse" function?'

    # Act
    use_case.execute(query)

    # Assert
    mock_graph_query_use_case.get_function_callers.assert_called_once_with("parse")
