"""
Unit tests for the CodeParser.
"""

import pytest

from src.domain.entities.graph_entities import (
    CallsEdge,
    ClassNode,
    ContainsEdge,
    FileNode,
    FunctionNode,
    ImportsEdge,
    NodeType,
)
from src.infrastructure.parser.code_parser import CodeParser

# A sample Python code snippet to be used for testing
SAMPLE_CODE = """
import os
from sys import argv

class MyClass:
    def __init__(self):
        pass

    def method_a(self):
        helper_function()

def helper_function():
    print("Hello")

class AnotherClass:
    pass

helper_function()
MyClass().method_a()
"""


@pytest.fixture(scope="module")
def parser() -> CodeParser:
    """Fixture to provide a CodeParser instance for the tests."""
    return CodeParser(language="python")


from src.domain.entities.graph_entities import ParsedData


@pytest.fixture(scope="module")
def parsed_data(parser: CodeParser) -> ParsedData:
    """Fixture to provide parsed data from the sample code."""
    file_path = "test_module.py"
    return parser.parse(file_path, SAMPLE_CODE)


def test_parser_initialization(parser: CodeParser) -> None:
    """Tests that the CodeParser initializes correctly."""
    assert parser is not None
    assert parser.parser is not None


def test_file_node_creation(parsed_data: ParsedData) -> None:
    """Tests that a FileNode is correctly created."""
    file_node = next((n for n in parsed_data.nodes if n.type == NodeType.FILE), None)
    assert file_node is not None
    assert isinstance(file_node, FileNode)
    assert file_node.id == "test_module.py"


def test_class_node_extraction(parsed_data: ParsedData) -> None:
    """Tests that class nodes are correctly extracted."""
    class_nodes = [n for n in parsed_data.nodes if isinstance(n, ClassNode)]
    assert len(class_nodes) == 2
    class_names = {node.properties["name"] for node in class_nodes}
    assert "MyClass" in class_names
    assert "AnotherClass" in class_names


def test_function_node_extraction(parsed_data: ParsedData) -> None:
    """Tests that function and method nodes are correctly extracted."""
    func_nodes = [n for n in parsed_data.nodes if isinstance(n, FunctionNode)]
    assert len(func_nodes) == 3
    func_names = {node.properties["name"] for node in func_nodes}
    assert "__init__" in func_names
    assert "method_a" in func_names
    assert "helper_function" in func_names


def test_contains_edge_creation(parsed_data: ParsedData) -> None:
    """Tests that CONTAINS edges from file to entities are created."""
    contains_edges = [e for e in parsed_data.edges if isinstance(e, ContainsEdge)]

    # Expected CONTAINS edges:
    # File -> MyClass
    # File -> AnotherClass
    # File -> helper_function
    # MyClass -> __init__
    # MyClass -> method_a
    # Total = 5
    assert len(contains_edges) == 5

    edge_map = {f"{edge.source_id} -> {edge.target_id}" for edge in contains_edges}

    # File level containment
    assert "test_module.py -> test_module.py::MyClass" in edge_map
    assert "test_module.py -> test_module.py::AnotherClass" in edge_map
    assert "test_module.py -> test_module.py::helper_function" in edge_map

    # Class level containment (methods)
    assert "test_module.py::MyClass -> test_module.py::__init__" in edge_map
    assert "test_module.py::MyClass -> test_module.py::method_a" in edge_map


def test_import_edge_extraction(parsed_data: ParsedData) -> None:
    """Tests that IMPORTS edges are correctly extracted."""
    import_edges = [e for e in parsed_data.edges if isinstance(e, ImportsEdge)]
    assert len(import_edges) == 2
    imported_modules = {edge.target_id for edge in import_edges}
    assert "os" in imported_modules
    assert "sys" in imported_modules


def test_call_edge_extraction(parsed_data: ParsedData) -> None:
    """Tests that CALLS edges are correctly extracted."""
    call_edges = [e for e in parsed_data.edges if isinstance(e, CallsEdge)]

    # Expected calls:
    # 1. helper_function() inside method_a -> source: test_module.py::method_a
    # 2. helper_function() at module level -> source: test_module.py
    # 3. MyClass().method_a() at module level -> source: test_module.py
    # Note: print() is not a defined function in the file, so it's ignored.
    assert len(call_edges) == 3

    calls_map = {f"{edge.source_id} -> {edge.target_id}" for edge in call_edges}

    # 1. Call from method_a to helper_function
    assert "test_module.py::method_a -> test_module.py::helper_function" in calls_map

    # 2. Call from module scope to helper_function
    assert "test_module.py -> test_module.py::helper_function" in calls_map

    # 3. Call from module scope to method_a
    assert "test_module.py -> test_module.py::method_a" in calls_map


def test_full_parse_node_and_edge_counts(parsed_data: ParsedData) -> None:
    """Checks the total number of nodes and edges from a full parse."""
    # 1 FileNode + 2 ClassNodes + 3 FunctionNodes = 6 nodes
    assert len(parsed_data.nodes) == 6

    # 5 ContainsEdges + 2 ImportsEdges + 3 CallsEdges = 10 edges
    assert len(parsed_data.edges) == 10
