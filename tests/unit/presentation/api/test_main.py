from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.presentation.api.main import app

client = TestClient(app)


@patch("src.presentation.api.main.PyGitHubClient")
@patch("src.presentation.api.main.ChromaDBClient")
@patch("src.presentation.api.main.OpenAIClient")
@patch("src.presentation.api.main.CreateIssueFromTextUseCase")
def test_analyze_and_create_issue_success(
    mock_use_case: MagicMock,
    mock_openai: MagicMock,
    mock_chroma: MagicMock,
    mock_github: MagicMock,
) -> None:
    # Arrange
    mock_use_case_instance = mock_use_case.return_value
    mock_use_case_instance.execute.return_value = "http://example.com/issue/1"

    # Act
    response = client.post(
        "/api/v1/analyze-and-create-issue",
        json={"text": "This is a test feedback."},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"issue_url": "http://example.com/issue/1"}
    mock_use_case_instance.execute.assert_called_once_with("This is a test feedback.")


@patch("src.presentation.api.main.PyGitHubClient")
@patch("src.presentation.api.main.ChromaDBClient")
@patch("src.presentation.api.main.OpenAIClient")
@patch("src.presentation.api.main.CreateIssueFromTextUseCase")
def test_analyze_and_create_issue_failure(
    mock_use_case: MagicMock,
    mock_openai: MagicMock,
    mock_chroma: MagicMock,
    mock_github: MagicMock,
) -> None:
    # Arrange
    mock_use_case_instance = mock_use_case.return_value
    mock_use_case_instance.execute.side_effect = Exception("Test error")

    # Act
    response = client.post(
        "/api/v1/analyze-and-create-issue",
        json={"text": "This is a test feedback."},
    )

    # Assert
    assert response.status_code == 500
    assert "An unexpected error occurred: Test error" in response.json()["detail"]
