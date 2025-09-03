"""
Utility classes and functions for repository name normalization and management.

This module provides utilities for converting repository names between different
formats required by various storage systems (ChromaDB, Neo4j).
"""

import re


class RepositoryNameNormalizer:
    """
    Utility class for normalizing repository names across different storage systems.

    This class handles conversion between different repository name formats:
    - GitHub URLs to standard owner/repo format
    - Standard names to ChromaDB collection names
    - Standard names to Neo4j labels
    - Reverse conversion for all formats
    """

    # GitHub URL patterns
    HTTPS_PATTERN = re.compile(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")
    SSH_PATTERN = re.compile(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$")

    # Character replacement patterns
    SPECIAL_CHARS_PATTERN = re.compile(r"[.\-/]")
    REPO_NAME_PATTERN = re.compile(r"^([^/]+)/([^/]+)$")

    @staticmethod
    def url_to_name(url: str) -> str:
        """
        Convert repository URL to standard name format (owner/repo).

        Args:
            url: Repository URL (HTTPS or SSH format)

        Returns:
            Repository name in owner/repo format

        Raises:
            ValueError: If URL format is invalid or not a GitHub URL
        """
        if not url or not isinstance(url, str):
            raise ValueError("Invalid repository URL: URL cannot be empty")

        # Try HTTPS pattern first
        match = RepositoryNameNormalizer.HTTPS_PATTERN.match(url.strip())
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}"

        # Try SSH pattern
        match = RepositoryNameNormalizer.SSH_PATTERN.match(url.strip())
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}"

        raise ValueError(f"Invalid repository URL: {url}")

    @staticmethod
    def to_collection_name(repo_name: str) -> str:
        """
        Convert repository name to ChromaDB collection name format.

        Args:
            repo_name: Repository name in owner/repo format

        Returns:
            ChromaDB collection name (repo_owner_repo_name)

        Raises:
            ValueError: If repository name format is invalid
        """
        if not repo_name or not isinstance(repo_name, str):
            raise ValueError("Repository name cannot be empty")

        if not RepositoryNameNormalizer.REPO_NAME_PATTERN.match(repo_name):
            raise ValueError("Repository name must contain owner/repo format")

        # Replace special characters with underscores
        normalized = RepositoryNameNormalizer.SPECIAL_CHARS_PATTERN.sub("_", repo_name)
        return f"repo_{normalized}"

    @staticmethod
    def to_neo4j_label(repo_name: str) -> str:
        """
        Convert repository name to Neo4j label format.

        Args:
            repo_name: Repository name in owner/repo format

        Returns:
            Neo4j label (Repo_owner_repo_name)

        Raises:
            ValueError: If repository name format is invalid
        """
        if not repo_name or not isinstance(repo_name, str):
            raise ValueError("Repository name cannot be empty")

        if not RepositoryNameNormalizer.REPO_NAME_PATTERN.match(repo_name):
            raise ValueError("Repository name must contain owner/repo format")

        # Replace special characters with underscores
        normalized = RepositoryNameNormalizer.SPECIAL_CHARS_PATTERN.sub("_", repo_name)
        return f"Repo_{normalized}"

    @staticmethod
    def from_collection_name(collection_name: str) -> str:
        """
        Convert ChromaDB collection name back to repository name format.

        Note: This performs a best-effort reconstruction. Due to the lossy nature
        of the normalization (multiple characters map to underscores), perfect
        reconstruction is not always possible.

        Args:
            collection_name: ChromaDB collection name (repo_owner_repo_name)

        Returns:
            Repository name in owner/repo format

        Raises:
            ValueError: If collection name format is invalid
        """
        if not collection_name or not isinstance(collection_name, str):
            raise ValueError("Collection name cannot be empty")

        if not collection_name.startswith("repo_"):
            raise ValueError("Invalid collection name format")

        # Remove prefix
        name_part = collection_name[5:]  # Remove "repo_" prefix

        # For reverse conversion, we need to use a mapping approach
        # since we can't perfectly reconstruct from underscores
        # This is a known limitation of the current approach

        # Split and try to find the owner/repo boundary
        parts = name_part.split("_")
        if len(parts) < 2:
            raise ValueError("Invalid collection name format")

        # Simple heuristic: assume first part is owner, rest is repo
        owner = parts[0]
        repo = "_".join(parts[1:])

        # Basic reconstruction - this is approximate
        result = f"{owner}/{repo}"

        # Apply some common transformations
        # Replace underscores with dashes (most common case)
        result = result.replace("_", "-")
        # But preserve the owner/repo separator
        result = result.replace("/-", "/")

        return result

    @staticmethod
    def from_neo4j_label(label: str) -> str:
        """
        Convert Neo4j label back to repository name format.

        Args:
            label: Neo4j label (Repo_owner_repo_name)

        Returns:
            Repository name in owner/repo format

        Raises:
            ValueError: If label format is invalid
        """
        if not label or not isinstance(label, str):
            raise ValueError("Label cannot be empty")

        if not label.startswith("Repo_"):
            raise ValueError("Invalid Neo4j label format")

        # Remove prefix and convert using collection name logic
        collection_equivalent = f"repo_{label[5:]}"  # Convert Repo_ to repo_
        return RepositoryNameNormalizer.from_collection_name(collection_equivalent)
