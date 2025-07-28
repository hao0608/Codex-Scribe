"""
This module provides a concrete implementation of the GitHubService using PyGithub.
"""

import logging
import os

from github import Github, GithubException
from github.Repository import Repository

from src.domain.services.github_service import (
    GitHubIssueDraft,
    GitHubService,
    GitHubServiceError,
)

logger = logging.getLogger(__name__)


class PyGitHubClient(GitHubService):
    """
    A client for interacting with the GitHub API using the PyGithub library.
    """

    def __init__(self, token: str | None = None, repo_name: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_name = repo_name or os.getenv("GITHUB_REPOSITORY")

        if not self.token:
            raise ValueError("GitHub token not provided or set in environment.")
        if not self.repo_name:
            raise ValueError(
                "GitHub repository name not provided or set in environment."
            )

        self.github = Github(self.token)
        self._repo = None

    def _get_repo(self) -> Repository:
        if self._repo is None:
            try:
                self._repo = self.github.get_repo(self.repo_name)
            except GithubException as e:
                logger.error("Failed to get repository '%s': %s", self.repo_name, e)
                raise GitHubServiceError(
                    f"Failed to access repository: {self.repo_name}"
                ) from e
        return self._repo

    def create_issue(self, draft: GitHubIssueDraft) -> str:
        """
        Creates a new issue in the configured GitHub repository.
        """
        try:
            repo = self._get_repo()
            logger.info("Creating issue '%s' in repo '%s'", draft.title, self.repo_name)
            issue = repo.create_issue(
                title=draft.title, body=draft.body, labels=draft.labels
            )
            logger.info("Successfully created issue #%d", issue.number)
            return issue.html_url
        except GithubException as e:
            logger.error(
                "Failed to create issue in repo '%s'. Error: %s", self.repo_name, e
            )
            raise GitHubServiceError("Failed to create GitHub issue.") from e
