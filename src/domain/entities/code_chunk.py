"""
This module defines the core domain entities for the Codex-Scribe project.
"""

import hashlib
from typing import Any

from pydantic import BaseModel, Field


class CodeChunk(BaseModel):
    """
    Represents a chunk of code from a source file, intended for embedding and retrieval.
    """

    id: str = Field(..., description="Unique identifier for the code chunk.")
    file_path: str = Field(..., description="The path to the source file.")
    content: str = Field(..., description="The actual content of the code chunk.")
    start_line: int = Field(
        ..., description="The starting line number of the chunk in the source file."
    )
    end_line: int = Field(
        ..., description="The ending line number of the chunk in the source file."
    )
    embedding: list[float] | None = Field(
        None, description="The vector embedding of the content."
    )
    metadata: dict[str, Any] = Field(
        {}, description="Additional metadata, e.g., language, class/function name."
    )

    @staticmethod
    def generate_id(file_path: str, content: str) -> str:
        """
        Generates a deterministic ID for a code chunk based on its content and path.
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{file_path}::{content_hash}"

    class Config:
        """Pydantic configuration."""

        frozen = True
        extra = "forbid"
