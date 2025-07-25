"""
This module provides text splitting functionalities, optimized for source code.
"""

from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.domain.entities.code_chunk import CodeChunk


class CodeTextSplitter:
    """
    A text splitter optimized for splitting source code into meaningful chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initializes the CodeTextSplitter.

        Args:
            chunk_size: The maximum size of a chunk (in characters).
            chunk_overlap: The number of characters to overlap between chunks.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # These separators are ordered from most important to least important
            # for splitting code.
            separators=["\nclass ", "\ndef ", "\n\tdef ", "\n\n", "\n", " ", ""],
            length_function=len,
        )

    def split(self, file_path: str, content: str) -> list[CodeChunk]:
        """
        Splits a file's content into a list of CodeChunk objects.

        Args:
            file_path: The path to the source file.
            content: The content of the file.

        Returns:
            A list of CodeChunk objects.
        """
        text_chunks = self.splitter.split_text(content)
        code_chunks: list[CodeChunk] = []

        for text_chunk in text_chunks:
            # This is a simplification. A more robust solution would find the
            # exact start and end lines of the chunk in the original content.
            # For now, we'll use placeholder line numbers.
            start_line = content.count("\n", 0, content.find(text_chunk)) + 1
            end_line = start_line + text_chunk.count("\n")

            chunk_id = CodeChunk.generate_id(file_path, text_chunk)
            metadata: dict[str, Any] = {
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
            }

            code_chunk = CodeChunk(
                id=chunk_id,
                file_path=file_path,
                content=text_chunk,
                start_line=start_line,
                end_line=end_line,
                metadata=metadata,
            )
            code_chunks.append(code_chunk)

        return code_chunks
