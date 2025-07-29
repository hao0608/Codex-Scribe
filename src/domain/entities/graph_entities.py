"""
This module defines the Pydantic models for the entities and relationships
in the code knowledge graph.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Enum for different types of nodes in the knowledge graph."""

    FILE = "File"
    CLASS = "Class"
    FUNCTION = "Function"


class EdgeType(str, Enum):
    """Enum for different types of edges (relationships) in the knowledge graph."""

    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"


class BaseNode(BaseModel):
    """Base model for a node in the knowledge graph."""

    id: str = Field(..., description="Unique identifier for the node.")
    type: NodeType = Field(..., description="The type of the node.")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="A dictionary of node properties."
    )


class FileNode(BaseNode):
    """Model for a file node."""

    type: NodeType = Field(default=NodeType.FILE, frozen=True)
    properties: dict[str, Any] = Field(default_factory=lambda: {"language": "python"})


class ClassNode(BaseNode):
    """Model for a class definition node."""

    type: NodeType = Field(default=NodeType.CLASS, frozen=True)


class FunctionNode(BaseNode):
    """Model for a function definition node."""

    type: NodeType = Field(default=NodeType.FUNCTION, frozen=True)


class BaseEdge(BaseModel):
    """Base model for an edge in the knowledge graph."""

    source_id: str = Field(..., description="The ID of the source node.")
    target_id: str = Field(..., description="The ID of the target node.")
    type: EdgeType = Field(..., description="The type of the edge.")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="A dictionary of edge properties."
    )


class ContainsEdge(BaseEdge):
    """Model for a CONTAINS relationship."""

    type: EdgeType = Field(default=EdgeType.CONTAINS, frozen=True)


class ImportsEdge(BaseEdge):
    """Model for an IMPORTS relationship."""

    type: EdgeType = Field(default=EdgeType.IMPORTS, frozen=True)


class CallsEdge(BaseEdge):
    """Model for a CALLS relationship."""

    type: EdgeType = Field(default=EdgeType.CALLS, frozen=True)


class ParsedData(BaseModel):
    """
    A container for all nodes and edges extracted from a single file.
    """

    file_path: str
    nodes: list[BaseNode]
    edges: list[BaseEdge]
