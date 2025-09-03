"""
Test cases for multi-repository ChromaDB client.

This module tests the ChromaDB client's ability to manage multiple
repository collections with proper isolation and management.
"""

import pytest
import tempfile
import shutil
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from src.domain.entities.code_chunk import CodeChunk
from src.infrastructure.database.multi_repo_chroma_client import MultiRepoChromaDBClient


class TestMultiRepoChromaDBClient:
    """Test suite for MultiRepoChromaDBClient class."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary directory for test database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def client(self, temp_db_path):
        """Create client instance for testing."""
        return MultiRepoChromaDBClient(path=temp_db_path)
    
    @pytest.fixture
    def sample_chunk(self):
        """Create sample code chunk for testing."""
        return CodeChunk(
            id="test-chunk-1",
            file_path="src/main.py",
            content="def hello(): return 'world'",
            start_line=1,
            end_line=1,
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            metadata={"language": "python", "lines": 1}
        )
    
    @pytest.fixture
    def another_chunk(self):
        """Create another sample code chunk for testing."""
        return CodeChunk(
            id="test-chunk-2", 
            file_path="src/utils.py",
            content="def process_data(data): return data.upper()",
            start_line=5,
            end_line=5,
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6],
            metadata={"language": "python", "lines": 1}
        )

    def test_add_chunk_to_specific_repository(self, client, sample_chunk):
        """Test adding code chunk to specific repository collection"""
        repo_name = "user/test-repo"
        
        # This should work without error
        client.add(sample_chunk, repo_name)
        
        # Verify chunk was added to correct collection
        results = client.query("hello", repo_name, top_k=1)
        assert len(results) == 1
        assert results[0]["content"] == sample_chunk.content
        assert results[0]["repository_name"] == repo_name
    
    def test_query_specific_repository(self, client, sample_chunk, another_chunk):
        """Test querying chunks from specific repository"""
        repo1 = "user/repo1"
        repo2 = "user/repo2"
        
        # Add chunks to different repositories
        client.add(sample_chunk, repo1)
        client.add(another_chunk, repo2)
        
        # Query specific repository
        results1 = client.query("hello", repo1, top_k=10)
        results2 = client.query("process", repo2, top_k=10)
        
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0]["content"] == sample_chunk.content
        assert results1[0]["repository_name"] == repo1
        assert results2[0]["content"] == another_chunk.content
        assert results2[0]["repository_name"] == repo2
    
    def test_repository_isolation(self, client, sample_chunk):
        """Test that repositories are completely isolated"""
        repo1 = "user/isolated1"
        repo2 = "user/isolated2"
        
        # Add chunk only to repo1
        client.add(sample_chunk, repo1)
        
        # Query repo2 should return no results
        results = client.query("hello", repo2, top_k=10)
        assert len(results) == 0
        
        # Query repo1 should return results
        results = client.query("hello", repo1, top_k=10)
        assert len(results) == 1
        assert results[0]["repository_name"] == repo1

    def test_list_repositories(self, client, sample_chunk, another_chunk):
        """Test listing all repositories with data"""
        repos = ["user/repo1", "user/repo2", "org/project"]
        
        # Add chunks to different repositories
        for i, repo in enumerate(repos):
            # Create new chunk since CodeChunk is frozen
            base_chunk = sample_chunk if i == 0 else another_chunk
            chunk = CodeChunk(
                id=f"chunk-{i}",
                file_path=base_chunk.file_path,
                content=base_chunk.content,
                start_line=base_chunk.start_line,
                end_line=base_chunk.end_line,
                embedding=base_chunk.embedding,
                metadata=base_chunk.metadata
            )
            client.add(chunk, repo)
        
        available_repos = client.list_repositories()
        assert set(available_repos) == set(repos)

    def test_delete_repository_collection(self, client, sample_chunk):
        """Test deleting entire repository collection"""
        repo_name = "user/temp-repo"
        
        # Add chunk to repository
        client.add(sample_chunk, repo_name)
        assert repo_name in client.list_repositories()
        
        # Delete repository
        client.delete_repository(repo_name)
        assert repo_name not in client.list_repositories()
        
        # Query should return no results
        results = client.query("hello", repo_name, top_k=10)
        assert len(results) == 0

    def test_get_repository_stats(self, client):
        """Test getting repository statistics"""
        repo_name = "user/stats-repo"
        
        # Add multiple chunks
        chunks = []
        for i in range(5):
            chunk = CodeChunk(
                id=f"chunk-{i}",
                file_path=f"src/file{i}.py",
                content=f"def func{i}(): pass",
                start_line=i + 1,
                end_line=i + 1,
                embedding=[0.1 * (i + 1), 0.2 * (i + 1), 0.3 * (i + 1), 0.4 * (i + 1), 0.5 * (i + 1)],
                metadata={"language": "python", "lines": 1}
            )
            chunks.append(chunk)
            client.add(chunk, repo_name)
        
        stats = client.get_repository_stats(repo_name)
        assert stats["chunk_count"] == 5
        assert stats["repository_name"] == repo_name
        assert "collection_name" in stats
        
    def test_query_multiple_repositories(self, client, sample_chunk, another_chunk):
        """Test querying across multiple repositories"""
        repos = ["user/repo1", "user/repo2", "user/repo3"]
        
        # Add chunks to repositories
        client.add(sample_chunk, repos[0])
        client.add(another_chunk, repos[1])
        
        # Query multiple repositories
        results = client.query_multiple("def", repos, top_k=10)
        
        # Should return results from both repositories
        assert len(results) == 2
        repo_names = [r["repository_name"] for r in results]
        assert set(repo_names) == {repos[0], repos[1]}

    def test_collection_name_normalization(self, client, sample_chunk):
        """Test that collection names are properly normalized"""
        repo_name = "user/repo-with-special.chars"
        
        client.add(sample_chunk, repo_name)
        
        # Check that collection was created with normalized name
        collections = client.list_collections()
        expected_collection_name = "repo_user_repo_with_special_chars"
        assert expected_collection_name in collections

    def test_add_without_embedding_raises_error(self, client):
        """Test that adding chunk without embedding raises error"""
        chunk_without_embedding = CodeChunk(
            id="no-embedding",
            file_path="test.py",
            content="print('test')",
            start_line=1,
            end_line=1,
            embedding=None,
            metadata={}
        )
        
        with pytest.raises(ValueError, match="CodeChunk must have an embedding"):
            client.add(chunk_without_embedding, "user/test-repo")

    def test_query_nonexistent_repository(self, client):
        """Test querying repository that doesn't exist"""
        results = client.query("test", "user/nonexistent", top_k=5)
        assert len(results) == 0

    def test_get_stats_nonexistent_repository(self, client):
        """Test getting stats for repository that doesn't exist"""
        stats = client.get_repository_stats("user/nonexistent")
        assert stats["chunk_count"] == 0
        assert stats["repository_name"] == "user/nonexistent"

    def test_concurrent_access(self, client, sample_chunk):
        """Test concurrent access to multiple repositories"""
        repos = [f"user/concurrent-repo-{i}" for i in range(3)]
        
        # Add chunks to multiple repositories
        for i, repo in enumerate(repos):
            # Create a new chunk for each repository since CodeChunk is frozen
            chunk = CodeChunk(
                id=f"concurrent-chunk-{i}",
                file_path=sample_chunk.file_path,
                content=sample_chunk.content,
                start_line=sample_chunk.start_line,
                end_line=sample_chunk.end_line,
                embedding=sample_chunk.embedding,
                metadata=sample_chunk.metadata
            )
            client.add(chunk, repo)
        
        # All repositories should be accessible
        for repo in repos:
            results = client.query("hello", repo, top_k=5)
            assert len(results) == 1
            assert results[0]["repository_name"] == repo

    def test_large_number_of_repositories(self, client, sample_chunk):
        """Test handling large number of repositories"""
        num_repos = 50
        repos = [f"user/repo-{i:03d}" for i in range(num_repos)]
        
        # Add chunks to many repositories
        for repo in repos:
            # Create a new chunk for each repository since CodeChunk is frozen
            chunk = CodeChunk(
                id=f"chunk-{repo.split('/')[-1]}",
                file_path=sample_chunk.file_path,
                content=sample_chunk.content,
                start_line=sample_chunk.start_line,
                end_line=sample_chunk.end_line,
                embedding=sample_chunk.embedding,
                metadata=sample_chunk.metadata
            )
            client.add(chunk, repo)
        
        # Verify all repositories are listed
        listed_repos = client.list_repositories()
        assert len(listed_repos) == num_repos
        assert set(listed_repos) == set(repos)

    def test_invalid_repository_names(self, client, sample_chunk):
        """Test handling invalid repository names"""
        invalid_names = [
            "",
            "no-slash",
            "too/many/slashes",
            "user/",
            "/repo"
        ]
        
        for invalid_name in invalid_names:
            with pytest.raises(ValueError):
                client.add(sample_chunk, invalid_name)