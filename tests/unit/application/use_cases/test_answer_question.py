"""
Unit tests for the AnswerQuestionUseCase, focusing on the hybrid query classifier.
"""

import json
from unittest.mock import MagicMock

import pytest

from src.application.use_cases.answer_question import AnswerQuestionUseCase
from src.application.use_cases.graph_query import GraphQueryUseCase
from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.infrastructure.llm.openai_client import OpenAIClient


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    """Fixture for a mocked EmbeddingService."""
    return MagicMock(spec=EmbeddingService)


@pytest.fixture
def mock_code_repository() -> MagicMock:
    """Fixture for a mocked CodeRepository."""
    return MagicMock(spec=CodeRepository)


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Fixture for a mocked OpenAIClient."""
    return MagicMock(spec=OpenAIClient)


@pytest.fixture
def mock_graph_query_use_case() -> MagicMock:
    """Fixture for a mocked GraphQueryUseCase."""
    return MagicMock(spec=GraphQueryUseCase)


@pytest.fixture
def answer_question_use_case(
    mock_embedding_service: MagicMock,
    mock_code_repository: MagicMock,
    mock_llm_client: MagicMock,
    mock_graph_query_use_case: MagicMock,
) -> AnswerQuestionUseCase:
    """Fixture for the AnswerQuestionUseCase with mocked dependencies."""
    return AnswerQuestionUseCase(
        embedding_service=mock_embedding_service,
        code_repository=mock_code_repository,
        llm_client=mock_llm_client,
        graph_query_use_case=mock_graph_query_use_case,
    )


@pytest.mark.unit
def test_classify_query_with_llm_success_for_callers(
    answer_question_use_case: AnswerQuestionUseCase, mock_llm_client: MagicMock
) -> None:
    """Tests successful LLM classification for a 'callers' query."""
    query = "Who calls the 'process_payment' function?"
    mock_response = {
        "type": "graph_query_callers",
        "entity": "process_payment",
        "confidence": 0.9,
    }
    mock_llm_client.get_chat_completion.return_value = json.dumps(mock_response)

    intent = answer_question_use_case._classify_query_intent(query)

    assert intent["type"] == "graph_query_callers"
    assert intent["entity"] == "process_payment"


@pytest.mark.unit
def test_classify_query_with_llm_success_for_vector_search(
    answer_question_use_case: AnswerQuestionUseCase, mock_llm_client: MagicMock
) -> None:
    """Tests successful LLM classification for a vector search query."""
    query = "How does authentication work?"
    mock_response = {"type": "vector_search", "entity": None, "confidence": 0.95}
    mock_llm_client.get_chat_completion.return_value = json.dumps(mock_response)

    intent = answer_question_use_case._classify_query_intent(query)

    assert intent["type"] == "vector_search"
    assert intent["entity"] is None


@pytest.mark.unit
def test_classify_query_fallback_to_regex_on_llm_failure(
    answer_question_use_case: AnswerQuestionUseCase, mock_llm_client: MagicMock
) -> None:
    """Tests fallback to regex when the LLM returns invalid JSON."""
    query = 'Who calls the "process_payment" function?'
    mock_llm_client.get_chat_completion.return_value = "This is not JSON"

    intent = answer_question_use_case._classify_query_intent(query)

    assert intent["type"] == "graph_query_callers"
    assert intent["entity"] == "process_payment"


@pytest.mark.unit
def test_classify_query_fallback_to_regex_on_low_confidence(
    answer_question_use_case: AnswerQuestionUseCase, mock_llm_client: MagicMock
) -> None:
    """Tests fallback to regex when LLM confidence is low."""
    query = 'What methods are in the "User" class?'
    mock_response = {
        "type": "graph_query_methods",
        "entity": "User",
        "confidence": 0.5,  # Below the 0.75 threshold
    }
    mock_llm_client.get_chat_completion.return_value = json.dumps(mock_response)

    intent = answer_question_use_case._classify_query_intent(query)

    assert intent["type"] == "graph_query_methods"
    assert intent["entity"] == "User"


@pytest.mark.unit
def test_classify_query_defaults_to_vector_search(
    answer_question_use_case: AnswerQuestionUseCase, mock_llm_client: MagicMock
) -> None:
    """Tests that the default classification is vector_search when all else fails."""
    query = "A very ambiguous query"
    mock_llm_client.get_chat_completion.return_value = None  # Simulate LLM error

    intent = answer_question_use_case._classify_query_intent(query)

    assert intent["type"] == "vector_search"
    assert intent["entity"] is None


@pytest.mark.unit
def test_get_optimal_top_k_for_simple_query(
    answer_question_use_case: AnswerQuestionUseCase,
) -> None:
    """Tests that a simple query results in a lower top_k."""
    simple_query = "What is the 'User' class?"
    top_k = answer_question_use_case._get_optimal_top_k(simple_query)
    assert top_k == 5


@pytest.mark.unit
def test_get_optimal_top_k_for_complex_query(
    answer_question_use_case: AnswerQuestionUseCase,
) -> None:
    """Tests that a complex query results in a higher top_k."""
    complex_query = (
        "How does the authentication system work, and why was it designed this way?"
    )
    top_k = answer_question_use_case._get_optimal_top_k(complex_query)
    assert top_k == 10
