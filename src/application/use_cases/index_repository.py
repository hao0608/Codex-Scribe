"""
This module contains the use case for indexing a code repository.
"""

from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.infrastructure.file_processor import FileProcessor
from src.infrastructure.text_splitter import CodeTextSplitter


class IndexRepositoryUseCase:
    """
    A use case for discovering, processing, and indexing all files in a repository.
    """

    def __init__(
        self,
        file_processor: FileProcessor,
        text_splitter: CodeTextSplitter,
        embedding_service: EmbeddingService,
        code_repository: CodeRepository,
    ):
        """
        Initializes the IndexRepositoryUseCase.

        Args:
            file_processor: An instance of FileProcessor to handle file operations.
            text_splitter: An instance of CodeTextSplitter to chunk documents.
            embedding_service: An instance of EmbeddingService to create embeddings.
            code_repository: An instance of CodeRepository to store the chunks.
        """
        self.file_processor = file_processor
        self.text_splitter = text_splitter
        self.embedding_service = embedding_service
        self.code_repository = code_repository

    def execute(self, directory_path: str) -> None:
        """
        Executes the repository indexing process.

        Args:
            directory_path: The path to the local repository to be indexed.
        """
        print(f"Starting to index repository at: {directory_path}")

        # 1. Discover and read all files
        file_contents = self.file_processor.read_files(directory_path)
        print(f"Found {len(file_contents)} files to process.")

        all_chunks = []
        for file_path, content in file_contents.items():
            if not content.strip():
                print(f"Skipping empty file: {file_path}")
                continue

            # 2. Split file content into chunks
            chunks = self.text_splitter.split(file_path, content)
            all_chunks.extend(chunks)

        if not all_chunks:
            print("No content to index.")
            return

        print(f"Generated {len(all_chunks)} code chunks.")

        # 3. Generate embeddings for all chunks in a batch
        chunk_contents = [chunk.content for chunk in all_chunks]
        embeddings = self.embedding_service.get_embeddings(chunk_contents)

        # 4. Assign embeddings back to chunks
        for i, chunk in enumerate(all_chunks):
            # Pydantic models are immutable, so we create a new instance
            # with the embedding.
            chunk_with_embedding = chunk.model_copy(update={"embedding": embeddings[i]})
            all_chunks[i] = chunk_with_embedding

        # 5. Add all chunks to the repository in a batch
        self.code_repository.add_batch(all_chunks)
        print(f"Successfully indexed {len(all_chunks)} chunks.")
