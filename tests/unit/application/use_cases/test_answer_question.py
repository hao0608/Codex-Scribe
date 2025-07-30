"""
Unit tests for the AnswerQuestionUseCase.
"""

from unittest.mock import MagicMock

import pytest

from src.application.use_cases.answer_question import AnswerQuestionUseCase
from src.application.use_cases.graph_query import GraphQueryUseCase
from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.infrastructure.llm.openai_client import OpenAIClient


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    return MagicMock(spec=EmbeddingService)


@pytest.fixture
def mock_code_repository() -> MagicMock:
    return MagicMock(spec=CodeRepository)


@pytest.fixture
def mock_llm_client() -> MagicMock:
    return MagicMock(spec=OpenAIClient)


@pytest.fixture
def mock_graph_query_use_case() -> MagicMock:
    return MagicMock(spec=GraphQueryUseCase)


@pytest.fixture
def answer_question_use_case(
    mock_embedding_service: MagicMock,
    mock_code_repository: MagicMock,
    mock_llm_client: MagicMock,
    mock_graph_query_use_case: MagicMock,
) -> AnswerQuestionUseCase:
    return AnswerQuestionUseCase(
        embedding_service=mock_embedding_service,
        code_repository=mock_code_repository,
        llm_client=mock_llm_client,
        graph_query_use_case=mock_graph_query_use_case,
    )


@pytest.mark.unit
def test_plan_task_routes_to_vector_search_by_default(
    answer_question_use_case: AnswerQuestionUseCase,
) -> None:
    """Tests that the default task is vector_search."""
    query = "How does authentication work?"
    task, params = answer_question_use_case._plan_task(query)
    assert task == "vector_search"
    assert params is None


@pytest.mark.unit
def test_plan_task_routes_to_graph_query_for_callers(
    answer_question_use_case: AnswerQuestionUseCase,
) -> None:
    """Tests routing for 'who calls' type questions."""
    query = 'Who calls the "process_payment" function?'
    task, params = answer_question_use_case._plan_task(query)
    assert task == "graph_query_callers"
    assert params == {"function_name": "process_payment"}


@pytest.mark.unit
def test_plan_task_routes_to_graph_query_for_methods(
    answer_question_use_case: AnswerQuestionUseCase,
) -> None:
    """Tests routing for 'methods in' type questions."""
    query = 'What methods are in the "User" class?'
    task, params = answer_question_use_case._plan_task(query)
    assert task == "graph_query_methods"
    assert params == {"class_name": "User"}
