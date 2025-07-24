"""
This module provides a client to interact with the OpenAI API.
"""

import os
from typing import cast

from openai import OpenAI

from src.domain.services.embedding_service import EmbeddingService


class OpenAIClient(EmbeddingService):
    """
    A client for interacting with the OpenAI API, implementing the EmbeddingService.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initializes the OpenAI client.

        Args:
            api_key: The OpenAI API key. If not provided, it will be read from
                     the OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or set in environment.")
        self.client = OpenAI(api_key=self.api_key)

    def get_embedding(
        self, text: str, model: str = "text-embedding-3-large"
    ) -> list[float]:
        """
        Creates an embedding for a single string of text.

        Args:
            text: The text to embed.
            model: The embedding model to use.

        Returns:
            A list of floats representing the vector embedding.
        """
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[text], model=model)
        return cast(list[float], response.data[0].embedding)

    def get_embeddings(
        self, texts: list[str], model: str = "text-embedding-3-large"
    ) -> list[list[float]]:
        """
        Creates embeddings for a batch of texts.

        Args:
            texts: A list of texts to embed.
            model: The embedding model to use.

        Returns:
            A list of vector embeddings.
        """
        texts = [text.replace("\n", " ") for text in texts]
        response = self.client.embeddings.create(input=texts, model=model)
        return [cast(list[float], item.embedding) for item in response.data]

    def get_chat_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        model: str = "gpt-4o",
    ) -> str | None:
        """
        Gets a chat completion from the OpenAI API.

        Args:
            prompt: The user's prompt.
            system_message: The system message to set the context for the assistant.
            model: The chat model to use.

        Returns:
            The content of the assistant's response, or None if no content is available.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )
        if response.choices and response.choices[0].message:
            return cast(str | None, response.choices[0].message.content)
        return None
