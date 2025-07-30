from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.create_issue_from_text import CreateIssueFromTextUseCase
from src.presentation.api.main import app, get_create_issue_use_case

client = TestClient(app)


@pytest.fixture
def mock_use_case() -> MagicMock:
    return MagicMock(spec=CreateIssueFromTextUseCase)


@pytest.mark.unit
def test_analyze_and_create_issue_success(mock_use_case: MagicMock) -> None:
    # Arrange
    mock_use_case.execute.return_value = "http://example.com/issue/1"
    app.dependency_overrides[get_create_issue_use_case] = lambda: mock_use_case

    # Act
    response = client.post(
        "/api/v1/analyze-and-create-issue",
        json={"text": "This is a test feedback."},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"issue_url": "http://example.com/issue/1"}
    mock_use_case.execute.assert_called_once_with("This is a test feedback.")

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.unit
def test_analyze_and_create_issue_failure(mock_use_case: MagicMock) -> None:
    # Arrange
    mock_use_case.execute.side_effect = Exception("Test error")
    app.dependency_overrides[get_create_issue_use_case] = lambda: mock_use_case

    # Act
    response = client.post(
        "/api/v1/analyze-and-create-issue",
        json={"text": "This is a test feedback."},
    )

    # Assert
    assert response.status_code == 500
    assert "An unexpected error occurred: Test error" in response.json()["detail"]

    # Clean up
    app.dependency_overrides.clear()
