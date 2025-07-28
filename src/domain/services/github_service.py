"""
This module defines the abstract interface for a GitHub service.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class GitHubIssueDraft(BaseModel):
    """
    A Pydantic model for GitHub issue drafts.
    """

    title: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="The title of the GitHub issue.",
    )
    body: str = Field(
        ...,
        min_length=50,
        description="The body of the GitHub issue, in Markdown format.",
    )
    labels: list[str] = Field(
        default_factory=lambda: ["ai-draft", "needs-review"],
        description="A list of labels to apply to the issue.",
    )


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
