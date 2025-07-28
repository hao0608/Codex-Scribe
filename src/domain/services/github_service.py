"""
This module defines the abstract interface for a GitHub service.
"""

from abc import ABC, abstractmethod

from src.domain.entities.github_issue_draft import GitHubIssueDraft


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
