"""
Test cases for repository name normalization utilities.

This module tests the conversion and normalization of repository names
across different storage systems (ChromaDB, Neo4j).
"""

import pytest
from src.infrastructure.repository_utils import RepositoryNameNormalizer


class TestRepositoryNameNormalizer:
    """Test suite for RepositoryNameNormalizer class."""
    
    def test_normalize_github_url_to_name(self):
        """Test converting GitHub URL to repository name"""
        normalizer = RepositoryNameNormalizer()
        
        # Test HTTPS URLs
        assert normalizer.url_to_name("https://github.com/user/repo-name") == "user/repo-name"
        assert normalizer.url_to_name("https://github.com/org/my.project") == "org/my.project"
        assert normalizer.url_to_name("https://github.com/test-user/test_repo.git") == "test-user/test_repo"
        
        # Test SSH URLs
        assert normalizer.url_to_name("git@github.com:user/private-repo.git") == "user/private-repo"
        assert normalizer.url_to_name("git@github.com:org/complex-name.project.git") == "org/complex-name.project"
        
        # Test URLs with trailing slashes
        assert normalizer.url_to_name("https://github.com/user/repo/") == "user/repo"
    
    def test_normalize_name_for_collection(self):
        """Test normalizing repository name for ChromaDB collection"""
        normalizer = RepositoryNameNormalizer()
        
        # Basic normalization
        assert normalizer.to_collection_name("user/repo-name") == "repo_user_repo_name"
        assert normalizer.to_collection_name("org/my.project") == "repo_org_my_project"
        assert normalizer.to_collection_name("test-user/test_repo") == "repo_test_user_test_repo"
        
        # Special character handling
        assert normalizer.to_collection_name("user-123/repo.test-name") == "repo_user_123_repo_test_name"
        assert normalizer.to_collection_name("org_name/project-v2.0") == "repo_org_name_project_v2_0"
    
    def test_normalize_name_for_neo4j_label(self):
        """Test normalizing repository name for Neo4j label"""
        normalizer = RepositoryNameNormalizer()
        
        # Basic normalization
        assert normalizer.to_neo4j_label("user/repo-name") == "Repo_user_repo_name"
        assert normalizer.to_neo4j_label("org/my.project") == "Repo_org_my_project"
        assert normalizer.to_neo4j_label("test-user/test_repo") == "Repo_test_user_test_repo"
        
        # Special character handling
        assert normalizer.to_neo4j_label("user-123/repo.test-name") == "Repo_user_123_repo_test_name"
    
    def test_invalid_repository_names(self):
        """Test handling of invalid repository names"""
        normalizer = RepositoryNameNormalizer()
        
        # Invalid URLs
        with pytest.raises(ValueError, match="Invalid repository URL"):
            normalizer.url_to_name("invalid-url")
        
        with pytest.raises(ValueError, match="Invalid repository URL"):
            normalizer.url_to_name("https://example.com/user/repo")
        
        with pytest.raises(ValueError, match="Invalid repository URL"):
            normalizer.url_to_name("https://github.com/user")  # Missing repo name
        
        # Empty or invalid repository names
        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            normalizer.to_collection_name("")
        
        with pytest.raises(ValueError, match="Repository name must contain owner/repo format"):
            normalizer.to_collection_name("repo-without-owner")
        
        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            normalizer.to_neo4j_label("")

    def test_reverse_normalization(self):
        """Test converting normalized names back to approximate original format"""
        normalizer = RepositoryNameNormalizer()
        
        # Test round-trip normalization for simple cases (should work perfectly)
        simple_names = [
            "user/repo-name",
            "org/simple-repo"
        ]
        
        for original in simple_names:
            collection_name = normalizer.to_collection_name(original)
            neo4j_label = normalizer.to_neo4j_label(original)
            
            reconstructed_from_collection = normalizer.from_collection_name(collection_name)
            reconstructed_from_label = normalizer.from_neo4j_label(neo4j_label)
            
            # For simple cases, reconstruction should be exact
            assert reconstructed_from_collection == original
            assert reconstructed_from_label == original
        
        # Test that reconstruction produces valid repository names (even if not identical)
        complex_names = [
            "org/my.project",
            "test-user/complex_repo.name-v2"
        ]
        
        for original in complex_names:
            collection_name = normalizer.to_collection_name(original)
            neo4j_label = normalizer.to_neo4j_label(original)
            
            reconstructed_from_collection = normalizer.from_collection_name(collection_name)
            reconstructed_from_label = normalizer.from_neo4j_label(neo4j_label)
            
            # Should produce valid repository names with owner/repo format
            assert "/" in reconstructed_from_collection
            assert "/" in reconstructed_from_label
            assert len(reconstructed_from_collection.split("/")) == 2
            assert len(reconstructed_from_label.split("/")) == 2

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        normalizer = RepositoryNameNormalizer()
        
        # Very long repository names
        long_name = "user-with-very-long-name/repository-with-extremely-long-name-that-might-cause-issues"
        collection_name = normalizer.to_collection_name(long_name)
        assert collection_name.startswith("repo_")
        
        # Verify reconstruction produces valid format (even if not identical)
        reconstructed = normalizer.from_collection_name(collection_name)
        assert "/" in reconstructed
        assert len(reconstructed.split("/")) == 2
        
        # Names with numbers and special sequences
        complex_name = "user123/repo-v2.0.1_beta"
        assert normalizer.to_collection_name(complex_name) == "repo_user123_repo_v2_0_1_beta"
        assert normalizer.to_neo4j_label(complex_name) == "Repo_user123_repo_v2_0_1_beta"

    def test_normalization_consistency(self):
        """Test that normalization is consistent across calls"""
        normalizer = RepositoryNameNormalizer()
        
        repo_name = "user/test-repo"
        
        # Multiple calls should return same result
        collection1 = normalizer.to_collection_name(repo_name)
        collection2 = normalizer.to_collection_name(repo_name)
        assert collection1 == collection2
        
        label1 = normalizer.to_neo4j_label(repo_name)
        label2 = normalizer.to_neo4j_label(repo_name)
        assert label1 == label2

    def test_case_sensitivity(self):
        """Test case sensitivity handling"""
        normalizer = RepositoryNameNormalizer()
        
        # GitHub repository names are case-sensitive
        assert normalizer.to_collection_name("User/Repo") == "repo_User_Repo"
        assert normalizer.to_collection_name("user/repo") == "repo_user_repo"
        
        # These should be different
        assert normalizer.to_collection_name("User/Repo") != normalizer.to_collection_name("user/repo")