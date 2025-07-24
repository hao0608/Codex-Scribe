"""
This module defines the abstract service interfaces for core business logic.
"""

from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """
    Abstract interface for a service that creates vector embeddings for text.
    """

    @abstractmethod
    def get_embedding(self, text: str) -> list[float]:
        """
        Creates an embedding for a single string of text.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the vector embedding.
        """
        raise NotImplementedError

    @abstractmethod
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Creates embeddings for a batch of texts.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of vector embeddings.
        """
        raise NotImplementedError
