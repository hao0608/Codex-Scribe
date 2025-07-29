"""
Unit tests for the GraphQueryUseCase.
"""

from unittest.mock import MagicMock

import pytest

from src.application.use_cases.graph_query import GraphQueryUseCase
from src.infrastructure.database.graph_db import Neo4jService


@pytest.fixture
def mock_neo4j_service() -> MagicMock:
    """Fixture for a mocked Neo4jService."""
    mock_service = MagicMock(spec=Neo4jService)
    mock_session = MagicMock()
    mock_service._driver.session.return_value.__enter__.return_value = mock_session
    return mock_service


def test_get_function_callers(mock_neo4j_service: MagicMock) -> None:
    """
    Tests that get_function_callers constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_neo4j_service)
    function_name = "test_func"

    # Act
    use_case.get_function_callers(function_name)

    # Assert
    mock_session = (
        mock_neo4j_service._driver.session.return_value.__enter__.return_value
    )
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE callee.name = $function_name" in call_args[0][0]
    assert call_args[0][1] == {"function_name": function_name}


def test_get_class_dependencies(mock_neo4j_service: MagicMock) -> None:
    """
    Tests that get_class_dependencies constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_neo4j_service)
    class_name = "TestClass"

    # Act
    use_case.get_class_dependencies(class_name)

    # Assert
    mock_session = (
        mock_neo4j_service._driver.session.return_value.__enter__.return_value
    )
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE c.name = $class_name" in call_args[0][0]
    assert call_args[0][1] == {"class_name": class_name}


def test_get_methods_in_class(mock_neo4j_service: MagicMock) -> None:
    """
    Tests that get_methods_in_class constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_neo4j_service)
    class_name = "TestClass"

    # Act
    use_case.get_methods_in_class(class_name)

    # Assert
    mock_session = (
        mock_neo4j_service._driver.session.return_value.__enter__.return_value
    )
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE c.name = $class_name" in call_args[0][0]
    assert call_args[0][1] == {"class_name": class_name}
