"""
This module provides a client to interact with a ChromaDB vector database.
"""

import chromadb
from chromadb.types import Collection

from src.domain.entities.code_chunk import CodeChunk
from src.domain.repositories.code_repository import CodeRepository


class ChromaDBClient(CodeRepository):
    """
    A client for interacting with ChromaDB, implementing the CodeRepository.
    """

    def __init__(
        self, path: str = "./data/chroma_db", collection_name: str = "code_chunks"
    ):
        """
        Initializes the ChromaDB client.

        Args:
            path: The path to the directory where ChromaDB should store its data.
            collection_name: The name of the collection to use.
        """
        self.client = chromadb.PersistentClient(path=path)
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add(self, chunk: CodeChunk) -> None:
        """
        Adds a single CodeChunk to the ChromaDB collection.

        Args:
            chunk: The CodeChunk object to add.
        """
        if not chunk.embedding:
            raise ValueError(
                "CodeChunk must have an embedding to be added to the repository."
            )

        self.collection.add(
            ids=[chunk.id],
            embeddings=[chunk.embedding],
            documents=[chunk.content],
            metadatas=[chunk.metadata],
        )

    def add_batch(self, chunks: list[CodeChunk]) -> None:
        """
        Adds a batch of CodeChunk objects to the ChromaDB collection.

        Args:
            chunks: A list of CodeChunk objects to add.
        """
        ids = [chunk.id for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks if chunk.embedding]
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        if len(embeddings) != len(chunks):
            raise ValueError("All CodeChunks in a batch must have an embedding.")

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def get_existing_chunk_ids(self, chunk_ids: list[str]) -> set[str]:
        """
        Retrieves the set of chunk IDs that already exist in the collection.

        Args:
            chunk_ids: A list of chunk IDs to check.

        Returns:
            A set of IDs that are present in the database.
        """
        if not chunk_ids:
            return set()

        results = self.collection.get(ids=chunk_ids, include=[])
        return set(results["ids"])

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[CodeChunk]:
        """
        Searches for the most similar CodeChunks in the ChromaDB collection.

        Args:
            query_embedding: The vector embedding of the search query.
            top_k: The number of most similar chunks to return.

        Returns:
            A list of the most relevant CodeChunk objects.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        retrieved_chunks: list[CodeChunk] = []
        if not results["ids"] or not results["documents"] or not results["metadatas"]:
            return retrieved_chunks

        for i, result_id in enumerate(results["ids"][0]):
            # ChromaDB returns metadata as a dict, but we need to reconstruct the CodeChunk
            # We don't have all the original fields, so we fill what we can.
            # This is a limitation when retrieving from a simple vector store.
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            chunk = CodeChunk(
                id=result_id,
                content=results["documents"][0][i] if results["documents"] else "",
                file_path=metadata.get("file_path", "unknown"),
                start_line=metadata.get("start_line", -1),
                end_line=metadata.get("end_line", -1),
                metadata=metadata,
            )
            retrieved_chunks.append(chunk)

        return retrieved_chunks
