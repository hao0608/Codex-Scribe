"""
Multi-repository ChromaDB client implementation.

This module provides a ChromaDB client that supports multiple repository
collections with proper isolation and management.
"""

from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from src.domain.entities.code_chunk import CodeChunk
from src.infrastructure.repository_utils import RepositoryNameNormalizer


class MultiRepoChromaDBClient:
    """
    ChromaDB client supporting multiple repository collections.

    Each repository gets its own collection to ensure complete data isolation.
    Collection names are normalized using RepositoryNameNormalizer.
    """

    def __init__(self, path: str = "./data/chroma_db"):
        """
        Initialize the multi-repository ChromaDB client.

        Args:
            path: Path to the ChromaDB persistent storage directory
        """
        self.client = chromadb.PersistentClient(path=path)
        self._collections: dict[str, Collection] = {}
        self._normalizer = RepositoryNameNormalizer()

    def _get_collection(self, repository_name: str) -> Collection:
        """
        Get or create collection for the specified repository.

        Args:
            repository_name: Repository name in owner/repo format

        Returns:
            ChromaDB collection for the repository

        Raises:
            ValueError: If repository name format is invalid
        """
        # Validate repository name format
        if not repository_name or "/" not in repository_name:
            raise ValueError("Invalid repository name format. Expected 'owner/repo'")

        parts = repository_name.split("/")
        if len(parts) != 2 or not all(part.strip() for part in parts):
            raise ValueError("Invalid repository name format. Expected 'owner/repo'")

        collection_name = self._normalizer.to_collection_name(repository_name)

        if collection_name not in self._collections:
            self._collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"repository_name": repository_name}
            )

        return self._collections[collection_name]

    def add(self, chunk: CodeChunk, repository_name: str) -> None:
        """
        Add a code chunk to the specified repository's collection.

        Args:
            chunk: The CodeChunk to add
            repository_name: Repository name in owner/repo format

        Raises:
            ValueError: If chunk has no embedding or repository name is invalid
        """
        if not chunk.embedding:
            raise ValueError(
                "CodeChunk must have an embedding to be added to the repository."
            )

        collection = self._get_collection(repository_name)

        # Add repository name to metadata
        metadata = dict(chunk.metadata) if chunk.metadata else {}
        metadata["repository_name"] = repository_name

        collection.add(
            ids=[chunk.id],
            embeddings=[chunk.embedding],
            documents=[chunk.content],
            metadatas=[metadata],
        )

    def query(
        self,
        query_text: str,
        repository_name: str,
        top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Query chunks from a specific repository.

        Args:
            query_text: Text to search for (will be searched in document content)
            repository_name: Repository name in owner/repo format
            top_k: Number of results to return

        Returns:
            List of matching chunks with metadata
        """
        try:
            collection = self._get_collection(repository_name)
        except ValueError:
            # Return empty results for invalid repository names
            return []

        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            return []

        # For now, use text-based search since we don't have an embedding service
        # In a real implementation, you'd convert query_text to embedding first
        try:
            # Use ChromaDB's built-in text search capability
            results = collection.query(
                query_texts=[query_text],
                n_results=min(top_k, count)
            )
        except Exception:
            # If text search fails, try to get all documents and filter manually
            all_results = collection.get()
            if not all_results["documents"]:
                return []

            # Simple text matching for test purposes
            matching_indices = []
            for i, doc in enumerate(all_results["documents"]):
                if query_text.lower() in doc.lower():
                    matching_indices.append(i)

            if not matching_indices:
                return []

            # Limit results
            matching_indices = matching_indices[:top_k]

            # Format results
            formatted_results = []
            for i in matching_indices:
                result = {
                    "id": all_results["ids"][i],
                    "content": all_results["documents"][i],
                    "metadata": all_results["metadatas"][i] if all_results["metadatas"] else {},
                    "distance": None,
                    "repository_name": repository_name
                }
                formatted_results.append(result)
            return formatted_results

        # Format results from normal query
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                # Handle metadata properly to avoid type issues
                metadata = {}
                if results["metadatas"] and results["metadatas"][0] and results["metadatas"][0][i]:
                    metadata = dict(results["metadatas"][0][i])

                result = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": metadata,
                    "distance": results["distances"][0][i] if results["distances"] and results["distances"][0] else None,
                    "repository_name": repository_name
                }
                formatted_results.append(result)

        return formatted_results

    def query_multiple(
        self,
        query_text: str,
        repository_names: list[str],
        top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Query chunks across multiple repositories.

        Args:
            query_text: Text to search for
            repository_names: List of repository names to search
            top_k: Total number of results to return across all repositories

        Returns:
            List of matching chunks from all repositories, sorted by relevance
        """
        all_results = []
        per_repo_k = max(1, top_k // len(repository_names)) if repository_names else top_k

        for repo_name in repository_names:
            repo_results = self.query(query_text, repo_name, per_repo_k)
            all_results.extend(repo_results)

        # Sort by distance (lower is better) if available
        if all_results and all_results[0].get("distance") is not None:
            all_results.sort(key=lambda x: x.get("distance", float('inf')))

        # Return top_k results
        return all_results[:top_k]

    def list_repositories(self) -> list[str]:
        """
        List all repositories that have data in ChromaDB.

        Returns:
            List of repository names in owner/repo format
        """
        repositories = []

        # Get all collections
        collections = self.client.list_collections()

        for collection in collections:
            # Skip non-repository collections
            if not collection.name.startswith("repo_"):
                continue

            try:
                # Get repository name from collection metadata
                if collection.metadata and "repository_name" in collection.metadata:
                    repositories.append(collection.metadata["repository_name"])
                else:
                    # Fallback: try to reconstruct from collection name
                    repo_name = self._normalizer.from_collection_name(collection.name)
                    repositories.append(repo_name)
            except ValueError:
                # Skip collections that can't be parsed
                continue

        return repositories

    def list_collections(self) -> list[str]:
        """
        List all collection names in ChromaDB.

        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [collection.name for collection in collections]

    def delete_repository(self, repository_name: str) -> bool:
        """
        Delete all data for a specific repository.

        Args:
            repository_name: Repository name in owner/repo format

        Returns:
            True if repository was deleted, False if it didn't exist
        """
        try:
            collection_name = self._normalizer.to_collection_name(repository_name)

            # Remove from cache
            if collection_name in self._collections:
                del self._collections[collection_name]

            # Delete collection from ChromaDB
            self.client.delete_collection(name=collection_name)
            return True

        except ValueError:
            # Invalid repository name
            return False
        except Exception:
            # Collection might not exist
            return False

    def get_repository_stats(self, repository_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific repository.

        Args:
            repository_name: Repository name in owner/repo format

        Returns:
            Dictionary with repository statistics
        """
        try:
            collection = self._get_collection(repository_name)
            count = collection.count()
            collection_name = self._normalizer.to_collection_name(repository_name)

            return {
                "repository_name": repository_name,
                "collection_name": collection_name,
                "chunk_count": count
            }
        except ValueError:
            # Invalid repository name or collection doesn't exist
            return {
                "repository_name": repository_name,
                "collection_name": None,
                "chunk_count": 0
            }
        except Exception:
            # Other errors (e.g., collection doesn't exist)
            return {
                "repository_name": repository_name,
                "collection_name": None,
                "chunk_count": 0
            }
