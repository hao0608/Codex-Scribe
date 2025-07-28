from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from src.domain.entities.github_issue_draft import GitHubIssueDraft
from src.domain.services.github_service import GitHubServiceError
from src.infrastructure.github.pygithub_client import PyGitHubClient


@patch("src.infrastructure.github.pygithub_client.Github")
@patch("os.getenv")
def test_pygithub_client_initialization_success(
    mock_getenv: MagicMock, mock_github: MagicMock
) -> None:
    mock_getenv.side_effect = ["fake_token", "fake_owner/fake_repo"]

    client = PyGitHubClient()

    assert client.token == "fake_token"
    assert client.repo_name == "fake_owner/fake_repo"
    mock_github.assert_called_once_with("fake_token")


@patch("os.getenv")
def test_pygithub_client_initialization_no_token(mock_getenv: MagicMock) -> None:
    mock_getenv.side_effect = [None, "fake_owner/fake_repo"]
    with pytest.raises(ValueError, match="GitHub token not provided"):
        PyGitHubClient()


@patch("os.getenv")
def test_pygithub_client_initialization_no_repo(mock_getenv: MagicMock) -> None:
    mock_getenv.side_effect = ["fake_token", None]
    with pytest.raises(ValueError, match="GitHub repository name not provided"):
        PyGitHubClient()


@patch("src.infrastructure.github.pygithub_client.Github")
@patch("os.getenv")
def test_get_repo_failure(mock_getenv: MagicMock, mock_github: MagicMock) -> None:
    mock_getenv.side_effect = ["fake_token", "fake_owner/fake_repo"]
    mock_github.return_value.get_repo.side_effect = GithubException(404, "Not Found")

    client = PyGitHubClient()

    with pytest.raises(GitHubServiceError, match="Failed to access repository"):
        client._get_repo()


@patch("src.infrastructure.github.pygithub_client.Github")
@patch("os.getenv")
def test_create_issue_success(mock_getenv: MagicMock, mock_github: MagicMock) -> None:
    mock_getenv.side_effect = ["fake_token", "fake_owner/fake_repo"]
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.html_url = "http://example.com/issue/1"
    mock_issue.number = 1
    mock_repo.create_issue.return_value = mock_issue
    mock_github.return_value.get_repo.return_value = mock_repo

    client = PyGitHubClient()
    draft = GitHubIssueDraft(
        title="This is a test title for the issue",
        body="This is a test body for the issue, which is sufficiently long.",
        labels=["bug"],
    )

    issue_url = client.create_issue(draft)

    assert issue_url == "http://example.com/issue/1"
    mock_github.return_value.get_repo.assert_called_once_with("fake_owner/fake_repo")
    mock_repo.create_issue.assert_called_once_with(
        title="This is a test title for the issue",
        body="This is a test body for the issue, which is sufficiently long.",
        labels=["bug"],
    )


@patch("src.infrastructure.github.pygithub_client.Github")
@patch("os.getenv")
def test_create_issue_failure(mock_getenv: MagicMock, mock_github: MagicMock) -> None:
    mock_getenv.side_effect = ["fake_token", "fake_owner/fake_repo"]
    mock_repo = MagicMock()
    mock_repo.create_issue.side_effect = GithubException(500, "Server Error")
    mock_github.return_value.get_repo.return_value = mock_repo

    client = PyGitHubClient()
    draft = GitHubIssueDraft(
        title="This is a test title for the issue",
        body="This is a test body for the issue, which is sufficiently long.",
        labels=["bug"],
    )

    with pytest.raises(GitHubServiceError, match="Failed to create GitHub issue"):
        client.create_issue(draft)
