"""
Unit tests for the GraphQueryUseCase.
"""

from unittest.mock import MagicMock

import pytest
from neo4j import Driver

from src.application.use_cases.graph_query import GraphQueryUseCase


@pytest.fixture
def mock_driver() -> MagicMock:
    """Fixture for a mocked Neo4j Driver."""
    mock_driver = MagicMock(spec=Driver)
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    return mock_driver


def test_get_function_callers(mock_driver: MagicMock) -> None:
    """
    Tests that get_function_callers constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_driver)
    function_name = "test_func"

    # Act
    use_case.get_function_callers(function_name)

    # Assert
    mock_session = mock_driver.session.return_value.__enter__.return_value
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE callee.name = $function_name" in call_args[0][0]
    assert call_args[0][1] == {"function_name": function_name}


def test_get_class_dependencies(mock_driver: MagicMock) -> None:
    """
    Tests that get_class_dependencies constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_driver)
    class_name = "TestClass"

    # Act
    use_case.get_class_dependencies(class_name)

    # Assert
    mock_session = mock_driver.session.return_value.__enter__.return_value
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE c.name = $class_name" in call_args[0][0]
    assert call_args[0][1] == {"class_name": class_name}


def test_get_methods_in_class(mock_driver: MagicMock) -> None:
    """
    Tests that get_methods_in_class constructs and executes the correct query.
    """
    # Arrange
    use_case = GraphQueryUseCase(mock_driver)
    class_name = "TestClass"

    # Act
    use_case.get_methods_in_class(class_name)

    # Assert
    mock_session = mock_driver.session.return_value.__enter__.return_value
    assert mock_session.run.call_count == 1
    call_args = mock_session.run.call_args
    assert "WHERE c.name = $class_name" in call_args[0][0]
    assert call_args[0][1] == {"class_name": class_name}
