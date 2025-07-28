from unittest.mock import MagicMock, patch

from src.application.use_cases.create_issue_from_text import CreateIssueFromTextUseCase
from src.domain.entities.github_issue_draft import GitHubIssueDraft


def test_create_issue_from_text_use_case() -> None:
    # Arrange
    mock_llm = MagicMock()
    mock_embedding_service = MagicMock()
    mock_code_repository = MagicMock()
    mock_github_service = MagicMock()

    use_case = CreateIssueFromTextUseCase(
        llm=mock_llm,
        embedding_service=mock_embedding_service,
        code_repository=mock_code_repository,
        github_service=mock_github_service,
    )

    text = "The login button is not working on the mobile app."
    expected_issue_url = "http://example.com/issue/1"

    mock_embedding_service.get_embedding.return_value = [0.1, 0.2, 0.3]
    mock_code_repository.search.return_value = []

    draft = GitHubIssueDraft(
        title="Login Button Not Working on Mobile App",
        body="The user reported that the login button is not working on the mobile app.",
        labels=["bug", "mobile"],
    )
    mock_github_service.create_issue.return_value = expected_issue_url

    # Act
    with patch(
        "langchain_core.runnables.base.RunnableSequence.invoke"
    ) as mock_chain_invoke:
        mock_chain_invoke.return_value = draft
        issue_url = use_case.execute(text)

    # Assert
    assert issue_url == expected_issue_url
    mock_embedding_service.get_embedding.assert_called_once_with(text)
    mock_code_repository.search.assert_called_once_with([0.1, 0.2, 0.3], top_k=5)
    mock_chain_invoke.assert_called_once()
    mock_github_service.create_issue.assert_called_once_with(draft)
