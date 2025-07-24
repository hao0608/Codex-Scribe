"""
This module contains the use case for indexing a code repository.
"""

import asyncio

from tqdm import tqdm

from src.domain.repositories.code_repository import CodeRepository
from src.infrastructure.file_processor import FileProcessor
from src.infrastructure.llm.openai_client import AsyncOpenAIClient
from src.infrastructure.text_splitter import CodeTextSplitter


class IndexRepositoryUseCase:
    """
    A use case for discovering, processing, and indexing all files in a repository.
    """

    def __init__(
        self,
        file_processor: FileProcessor,
        text_splitter: CodeTextSplitter,
        embedding_client: AsyncOpenAIClient,
        code_repository: CodeRepository,
    ):
        """
        Initializes the IndexRepositoryUseCase.
        """
        self.file_processor = file_processor
        self.text_splitter = text_splitter
        self.embedding_client = embedding_client
        self.code_repository = code_repository

    async def execute(self, directory_path: str) -> None:
        """
        Executes the repository indexing process asynchronously.
        """
        print(f"Starting to index repository at: {directory_path}")

        file_contents = self.file_processor.read_files(directory_path)
        print(f"Found {len(file_contents)} files to process.")

        all_chunks = []
        for file_path, content in file_contents.items():
            if not content.strip():
                continue
            chunks = self.text_splitter.split(file_path, content)
            all_chunks.extend(chunks)

        if not all_chunks:
            print("No content to index.")
            return

        print(f"Generated {len(all_chunks)} code chunks.")

        batch_size = 200  # OpenAI API batch size limit

        tasks = []
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i : i + batch_size]
            chunk_contents = [chunk.content for chunk in batch_chunks]
            tasks.append(self.embedding_client.get_embeddings_async(chunk_contents))

        print(f"Sending {len(tasks)} batches to OpenAI API...")

        all_embeddings = []
        # Use tqdm for progress bar
        for f in tqdm(
            asyncio.as_completed(tasks), total=len(tasks), desc="Generating Embeddings"
        ):
            embeddings_batch = await f
            all_embeddings.extend(embeddings_batch)

        chunks_with_embeddings = []
        for i, chunk in enumerate(all_chunks):
            chunk_with_embedding = chunk.model_copy(
                update={"embedding": all_embeddings[i]}
            )
            chunks_with_embeddings.append(chunk_with_embedding)

        print("Adding chunks to the vector store...")
        # Add to repository in batches as well to be memory efficient
        for i in tqdm(
            range(0, len(chunks_with_embeddings), batch_size), desc="Storing Chunks"
        ):
            batch_to_store = chunks_with_embeddings[i : i + batch_size]
            self.code_repository.add_batch(batch_to_store)

        print(f"Successfully indexed {len(all_chunks)} chunks in total.")
