"""
This module provides clients to interact with the OpenAI API, both sync and async.
"""

import asyncio
import os

from openai import AsyncOpenAI, OpenAI

from src.domain.services.embedding_service import EmbeddingService


class OpenAIClient(EmbeddingService):
    """
    A synchronous client for interacting with the OpenAI API.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or set in environment.")
        self.client = OpenAI(api_key=self.api_key)

    def get_embedding(
        self, text: str, model: str = "text-embedding-3-small"
    ) -> list[float]:
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    def get_embeddings(
        self, texts: list[str], model: str = "text-embedding-3-small"
    ) -> list[list[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        response = self.client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]

    def get_chat_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        model: str = "gpt-4o",
    ) -> str | None:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content
        return None


class AsyncOpenAIClient(EmbeddingService):
    """
    An asynchronous client for interacting with the OpenAI API.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or set in environment.")
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def get_embedding(self, text: str) -> list[float]:
        # This remains synchronous as it's not the primary use case for async.
        # A truly async implementation would use the async client here as well.
        sync_client = OpenAI(api_key=self.api_key)
        response = sync_client.embeddings.create(
            input=[text.replace("\n", " ")], model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def get_embeddings_async(
        self, texts: list[str], model: str = "text-embedding-3-small"
    ) -> list[list[float]]:
        """
        Asynchronously creates embeddings for a batch of texts.
        """
        texts = [text.replace("\n", " ") for text in texts]
        response = await self.async_client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]

    def get_embeddings(
        self, texts: list[str], model: str = "text-embedding-3-small"
    ) -> list[list[float]]:
        """
        Synchronous wrapper for the async embedding generation for interface compatibility.
        """
        return asyncio.run(self.get_embeddings_async(texts, model))
