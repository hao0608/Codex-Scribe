"""
This module provides a CodeParser class to parse source code using tree-sitter
and extract structural information to build a knowledge graph.
"""

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser, Query, QueryCursor

from src.domain.entities.graph_entities import (
    BaseEdge,
    BaseNode,
    CallsEdge,
    ClassNode,
    ContainsEdge,
    FileNode,
    FunctionNode,
    ImportsEdge,
    ParsedData,
)

# --- Tree-sitter Queries ---
# These queries are used to find specific patterns in the AST.

# Finds all import statements
# e.g., `import os`, `from sys import argv`
IMPORT_QUERY = """
(import_statement) @import
(import_from_statement) @import_from
"""

# Finds class definitions
# e.g., `class MyClass:`, `@dataclass class MyData:`
CLASS_QUERY = """
(class_definition
  name: (identifier) @class.name) @class.definition
(decorated_definition
  definition: (class_definition
    name: (identifier) @class.name)) @class.definition
"""

# Finds function and method definitions
# e.g., `def my_func():`, `async def my_async_func():`
FUNCTION_QUERY = """
(function_definition
  name: (identifier) @function.name) @function.definition
(decorated_definition
  definition: (function_definition
    name: (identifier) @function.name)) @function.definition
"""

# Finds function calls
# e.g., `my_func()`, `self.method()`, `module.function()`
CALL_QUERY = """
(call
  function: [
    (identifier) @call.name
    (attribute attribute: (identifier) @call.name)
  ]) @call.expression
"""


class CodeParser:
    """
    Parses source code to extract entities and relationships for the knowledge graph.
    """

    def __init__(self, language: str = "python"):
        """
        Initializes the parser with a specific language.
        """
        try:
            if language != "python":
                raise ValueError("Currently only 'python' language is supported.")

            self.language = Language(tspython.language())
            self.parser = Parser(self.language)
        except Exception as e:
            print(f"Error initializing CodeParser with language '{language}': {e}")
            print(
                "Please ensure tree-sitter and tree-sitter-python are installed correctly."
            )
            raise

    def parse(self, file_path: str, content: str) -> ParsedData:
        """
        Parses a single file and extracts all nodes and edges.

        Args:
            file_path: The path to the file being parsed.
            content: The source code content of the file.

        Returns:
            A ParsedData object containing all extracted nodes and edges.
        """
        tree = self.parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node

        nodes: dict[str, BaseNode] = {}
        edges: list[BaseEdge] = []

        # Temporary map to hold non-serializable node objects for scope analysis
        node_map: dict[str, Node] = {}

        # 1. Create File Node
        file_id = file_path
        nodes[file_id] = FileNode(id=file_id, properties={"path": file_path})

        # 2. Extract all entities and their primary containment
        class_nodes = self._extract_classes(root_node, file_id)
        for class_node in class_nodes:
            nodes[class_node.id] = class_node
            edges.append(ContainsEdge(source_id=file_id, target_id=class_node.id))

        function_nodes = self._extract_functions(root_node, file_id, node_map)
        for func_node in function_nodes:
            nodes[func_node.id] = func_node

            # Determine if the function is a method of a class
            ts_node = node_map.get(func_node.id)
            if ts_node:
                scope_id = self._find_containing_scope(file_id, ts_node)
                # If the scope is a class, the class contains the method
                if scope_id in nodes and isinstance(nodes[scope_id], ClassNode):
                    edges.append(
                        ContainsEdge(source_id=scope_id, target_id=func_node.id)
                    )
                else:
                    # Only add file containment if it's not a class method
                    edges.append(
                        ContainsEdge(source_id=file_id, target_id=func_node.id)
                    )

        # 3. Extract relationships (Imports, Calls)
        import_edges = self._extract_imports(root_node, file_id)
        call_edges = self._extract_calls(root_node, file_id, list(nodes.keys()))

        edges.extend(import_edges)
        edges.extend(call_edges)

        return ParsedData(file_path=file_path, nodes=list(nodes.values()), edges=edges)

    def _execute_query(self, node: Node, query_str: str) -> dict[str, list[Node]]:
        """Helper to execute a tree-sitter query."""
        query = Query(self.language, query_str)
        cursor = QueryCursor(query)
        captures = cursor.captures(node)
        return captures

    def _extract_classes(self, root_node: Node, file_id: str) -> list[ClassNode]:
        """Extracts class nodes from the AST."""
        nodes = []
        captures = self._execute_query(root_node, CLASS_QUERY)
        if "class.name" in captures:
            for node in captures["class.name"]:
                class_name = node.text.decode("utf8")
                class_id = f"{file_id}::{class_name}"
                nodes.append(ClassNode(id=class_id, properties={"name": class_name}))
        return nodes

    def _extract_functions(
        self, root_node: Node, file_id: str, node_map: dict[str, Node]
    ) -> list[FunctionNode]:
        """Extracts function nodes from the AST."""
        nodes = []
        seen_func_ids = set()
        captures = self._execute_query(root_node, FUNCTION_QUERY)

        # Note: "function.definition" is used to get the whole function node for scope analysis
        func_definitions = captures.get("function.definition", [])

        for func_def_node in func_definitions:
            name_node = func_def_node.child_by_field_name("name")
            if name_node:
                func_name = name_node.text.decode("utf8")
                func_id = f"{file_id}::{func_name}"

                if func_id not in seen_func_ids:
                    # Do not store the non-serializable node object in properties
                    nodes.append(
                        FunctionNode(
                            id=func_id,
                            properties={"name": func_name},
                        )
                    )
                    # Store the tree-sitter node in a temporary map for scope analysis
                    node_map[func_id] = func_def_node
                    seen_func_ids.add(func_id)
        return nodes

    def _extract_imports(self, root_node: Node, file_id: str) -> list[ImportsEdge]:
        """Extracts import relationships from the AST."""
        edges = []
        captures = self._execute_query(root_node, IMPORT_QUERY)
        for _, nodes in captures.items():
            for node in nodes:
                text = node.text.decode("utf8")
                if text.startswith("from"):
                    module_name = text.split(" import ")[0].replace("from ", "").strip()
                else:
                    module_name = text.replace("import ", "").split(" as ")[0].strip()

                # This is a simplified import resolution.
                # In a real scenario, this would need to resolve relative vs. absolute imports.
                target_id = module_name
                edges.append(ImportsEdge(source_id=file_id, target_id=target_id))
        return edges

    def _find_containing_scope(self, file_id: str, node: Node) -> str:
        """
        Finds the containing function or class for a given node.
        Traverses up the AST from the given node.
        """
        current = node.parent
        while current:
            if current.type == "function_definition":
                name_node = current.child_by_field_name("name")
                if name_node:
                    return f"{file_id}::{name_node.text.decode('utf8')}"
            elif current.type == "class_definition":
                name_node = current.child_by_field_name("name")
                if name_node:
                    return f"{file_id}::{name_node.text.decode('utf8')}"
            current = current.parent
        return file_id  # Default to file scope

    def _extract_calls(
        self, root_node: Node, file_id: str, existing_node_ids: list[str]
    ) -> list[CallsEdge]:
        """Extracts function call relationships from the AST."""
        edges = []
        captures = self._execute_query(root_node, CALL_QUERY)

        call_expressions = captures.get("call.expression", [])

        # Get all class names defined in the file to filter out instantiations
        class_nodes = self._extract_classes(root_node, file_id)
        class_names = {node.properties["name"] for node in class_nodes}

        seen_edges = set()

        for call_node in call_expressions:
            # Find the name of the function being called
            name_node = call_node.child_by_field_name("function")
            if not name_node:
                continue

            call_name = ""
            if name_node.type == "identifier":
                call_name = name_node.text.decode("utf8")
            elif name_node.type == "attribute":
                # This handles method calls like `obj.method()`
                attr_node = name_node.child_by_field_name("attribute")
                if attr_node:
                    call_name = attr_node.text.decode("utf8")

            if not call_name:
                continue

            # Exclude class instantiations
            if call_name in class_names:
                continue

            # Determine the source and target of the call
            source_id = self._find_containing_scope(file_id, call_node)
            target_id = f"{file_id}::{call_name}"

            # Add edge if the target is a known function/method in the file
            edge_key = (source_id, target_id)
            if (
                target_id in existing_node_ids
                and source_id != target_id
                and edge_key not in seen_edges
            ):
                edges.append(CallsEdge(source_id=source_id, target_id=target_id))
                seen_edges.add(edge_key)

        return edges
