"""
This module contains the use case for indexing a code repository.
"""

import asyncio

from tqdm.asyncio import tqdm_asyncio

from src.domain.entities.code_chunk import CodeChunk
from src.infrastructure.database.chroma_client import ChromaDBClient
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
        code_repository: ChromaDBClient,  # Type hint specifically for get_existing_chunk_ids
    ):
        self.file_processor = file_processor
        self.text_splitter = text_splitter
        self.embedding_client = embedding_client
        self.code_repository = code_repository

    async def execute(
        self, directory_path: str, include_dirs: list[str] | None = None
    ) -> None:
        """
        Executes the repository indexing process with resume capability.
        """
        try:
            print(f"Starting to index repository at: {directory_path}")
            if include_dirs:
                print(f"Only including directories: {', '.join(include_dirs)}")

            file_contents = self.file_processor.read_files(directory_path, include_dirs)
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

            print(f"Generated {len(all_chunks)} total code chunks.")

            # --- Resume Logic ---
            all_chunk_ids = [chunk.id for chunk in all_chunks]
            existing_ids = self.code_repository.get_existing_chunk_ids(all_chunk_ids)

            unindexed_chunks = [
                chunk for chunk in all_chunks if chunk.id not in existing_ids
            ]

            if not unindexed_chunks:
                print("All chunks are already indexed. Nothing to do.")
                return

            print(
                f"{len(existing_ids)} chunks already indexed. Resuming with {len(unindexed_chunks)} new chunks."
            )
            # --- End of Resume Logic ---

            batch_size = 200
            semaphore = asyncio.Semaphore(5)  # Reduced concurrency

            async def get_embeddings_for_batch(
                batch: list[CodeChunk],
            ) -> list[CodeChunk]:
                async with semaphore:
                    contents = [chunk.content for chunk in batch]
                    embeddings = await self.embedding_client.get_embeddings_async(
                        contents
                    )

                    processed_batch = []
                    for i, chunk in enumerate(batch):
                        processed_batch.append(
                            chunk.model_copy(update={"embedding": embeddings[i]})
                        )

                    # Store immediately after processing
                    self.code_repository.add_batch(processed_batch)
                    return processed_batch

            tasks = []
            for i in range(0, len(unindexed_chunks), batch_size):
                batch_to_process = unindexed_chunks[i : i + batch_size]
                tasks.append(get_embeddings_for_batch(batch_to_process))

            print(
                f"Sending {len(tasks)} batches to OpenAI API with controlled concurrency..."
            )

            await tqdm_asyncio.gather(*tasks, desc="Indexing Batches")

            print(
                f"Successfully indexed {len(unindexed_chunks)} new chunks. Total indexed: {len(all_chunks)}."
            )
        except FileNotFoundError as e:
            print(f"Error: Directory not found at {directory_path}. Details: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during indexing: {e}")
            # In a real app, you might want to log this with more detail.
            # For now, we re-raise to let the caller handle it.
            raise
