"""
This module defines the abstract interface for a GitHub service.
"""

from abc import ABC, abstractmethod


class GitHubIssueDraft:
    """
    A simple data class for GitHub issue drafts.
    We will replace this with a Pydantic model in a later stage.
    """

    def __init__(self, title: str, body: str, labels: list[str]):
        self.title = title
        self.body = body
        self.labels = labels


class GitHubService(ABC):
    """
    Abstract base class for a service that interacts with GitHub.
    """

    @abstractmethod
    def create_issue(self, draft: GitHubIssueDraft) -> str:
        """
        Creates a new issue in a GitHub repository.

        Args:
            draft: An object containing the title, body, and labels for the issue.

        Returns:
            The URL of the newly created issue.

        Raises:
            GitHubServiceError: If the issue creation fails.
        """
        pass


class GitHubServiceError(Exception):
    """Custom exception for GitHub service errors."""

    pass
