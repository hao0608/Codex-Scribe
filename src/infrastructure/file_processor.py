"""
This module provides utilities for processing files from the local filesystem.
"""

import fnmatch
import os
from collections.abc import Iterator
from pathlib import Path


class FileProcessor:
    """
    A utility class for discovering and reading files from a directory.
    """

    DEFAULT_EXCLUDE_PATTERNS = {
        "**/__pycache__/*",
        "**/.git/*",
        "**/.pytest_cache/*",
        "**/node_modules/*",
        "**/.venv/*",
        "**/venv/*",
        "**/data/*",
        "**/.chroma/*",
        "**/*.pyc",
    }

    def __init__(
        self,
        supported_extensions: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ):
        """
        Initializes the FileProcessor.
        """
        if supported_extensions is None:
            self.supported_extensions = {
                ".py",
                ".md",
                ".js",
                ".ts",
                ".tsx",
                ".jsx",
                ".html",
                ".css",
                ".java",
                ".c",
                ".cpp",
                ".h",
                ".hpp",
                ".cs",
                ".go",
                ".rs",
                ".php",
                ".rb",
                ".swift",
                ".kt",
                ".scala",
                ".sh",
                ".toml",
                ".yaml",
                ".yml",
            }
        else:
            self.supported_extensions = set(supported_extensions)

        self.exclude_patterns = set(exclude_patterns or self.DEFAULT_EXCLUDE_PATTERNS)

    def _is_excluded(self, file_path: str) -> bool:
        """Checks if a file path matches any of the exclude patterns."""
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def discover_files(
        self, directory_path: str, include_dirs: list[str] | None = None
    ) -> Iterator[str]:
        """
        Recursively discovers all supported files in a given directory, with filtering.
        """
        base_paths = (
            [os.path.join(directory_path, d) for d in include_dirs]
            if include_dirs
            else [directory_path]
        )

        for base_path in base_paths:
            for root, _, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if Path(
                        file
                    ).suffix in self.supported_extensions and not self._is_excluded(
                        file_path
                    ):
                        yield file_path

    def read_file(self, file_path: str) -> str | None:
        """
        Reads the content of a single file.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None

    def read_files(
        self, directory_path: str, include_dirs: list[str] | None = None
    ) -> dict[str, str]:
        """
        Discovers and reads all supported files in a directory.
        """
        file_contents = {}
        for file_path in self.discover_files(directory_path, include_dirs):
            content = self.read_file(file_path)
            if content is not None:
                file_contents[file_path] = content
        return file_contents
