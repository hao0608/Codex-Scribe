"""
This module provides utilities for processing files from the local filesystem.
"""

import os
from collections.abc import Iterator
from pathlib import Path


class FileProcessor:
    """
    A utility class for discovering and reading files from a directory.
    """

    def __init__(self, supported_extensions: list[str] | None = None):
        """
        Initializes the FileProcessor.

        Args:
            supported_extensions: A list of file extensions to include.
                                  If None, defaults to a standard set of code/text files.
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

    def discover_files(self, directory_path: str) -> Iterator[str]:
        """
        Recursively discovers all supported files in a given directory.

        Args:
            directory_path: The path to the directory to scan.

        Yields:
            The path to each supported file found.
        """
        for root, _, files in os.walk(directory_path):
            for file in files:
                if Path(file).suffix in self.supported_extensions:
                    yield os.path.join(root, file)

    def read_file(self, file_path: str) -> str | None:
        """
        Reads the content of a single file.

        Args:
            file_path: The path to the file.

        Returns:
            The content of the file as a string, or None if an error occurs.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            # Log this error in a real application
            return None

    def read_files(self, directory_path: str) -> dict[str, str]:
        """
        Discovers and reads all supported files in a directory.

        Args:
            directory_path: The path to the directory to scan.

        Returns:
            A dictionary mapping file paths to their content.
        """
        file_contents = {}
        for file_path in self.discover_files(directory_path):
            content = self.read_file(file_path)
            if content is not None:
                file_contents[file_path] = content
        return file_contents
