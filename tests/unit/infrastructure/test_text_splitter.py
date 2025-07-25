"""
Unit tests for the CodeTextSplitter class.
"""

from src.domain.entities.code_chunk import CodeChunk
from src.infrastructure.text_splitter import CodeTextSplitter


def test_split_simple_python_code() -> None:
    """Tests splitting a simple Python code snippet."""
    splitter = CodeTextSplitter(chunk_size=50, chunk_overlap=0)
    code = "def hello():\n    print('hello')\n\nclass MyClass:\n    pass"
    chunks = splitter.split("test.py", code)

    assert len(chunks) > 1
    assert isinstance(chunks[0], CodeChunk)
    assert chunks[0].content.startswith("def hello():")
    assert chunks[1].content.startswith("class MyClass:")


def test_chunk_id_is_deterministic() -> None:
    """Tests that the generated chunk ID is deterministic."""
    splitter = CodeTextSplitter()
    code = "def my_function():\n    return 1"

    chunks1 = splitter.split("test.py", code)
    chunks2 = splitter.split("test.py", code)

    assert len(chunks1) == 1
    assert len(chunks2) == 1
    assert chunks1[0].id == chunks2[0].id


def test_line_numbers_are_calculated() -> None:
    """Tests that start and end line numbers are calculated correctly."""
    splitter = CodeTextSplitter(chunk_size=50, chunk_overlap=0)
    code = (
        "line 1\nline 2\nline 3\n\nclass MyClass:\n    def method(self):\n        pass"
    )
    chunks = splitter.split("test.py", code)

    assert len(chunks) > 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line >= 3
    assert chunks[1].start_line >= 5
