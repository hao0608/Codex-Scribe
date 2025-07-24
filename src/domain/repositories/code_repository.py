"""
This module defines the abstract repository interfaces for data access.
"""

from abc import ABC, abstractmethod

from src.domain.entities.code_chunk import CodeChunk


class CodeRepository(ABC):
    """
    Abstract interface for a repository that stores and retrieves CodeChunk objects.
    """

    @abstractmethod
    def add(self, chunk: CodeChunk) -> None:
        """
        Adds a single CodeChunk to the repository.

        Args:
            chunk: The CodeChunk object to add.
        """
        raise NotImplementedError

    @abstractmethod
    def add_batch(self, chunks: list[CodeChunk]) -> None:
        """
        Adds a batch of CodeChunk objects to the repository.

        Args:
            chunks: A list of CodeChunk objects to add.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[CodeChunk]:
        """
        Searches for the most similar CodeChunks based on a query embedding.

        Args:
            query_embedding: The vector embedding of the search query.
            top_k: The number of most similar chunks to return.

        Returns:
            A list of the most relevant CodeChunk objects.
        """
        raise NotImplementedError
