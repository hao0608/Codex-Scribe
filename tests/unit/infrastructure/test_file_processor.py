"""
Unit tests for the FileProcessor class.
"""

from pathlib import Path

import pytest

from src.infrastructure.file_processor import FileProcessor


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Creates a temporary directory structure for testing."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "src" / "utils.js").write_text("console.log('hello');")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "db.sqlite").write_text("data")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("config")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.pyc").write_text("cache")
    return tmp_path


@pytest.mark.unit
def test_discover_files_default(temp_repo: Path) -> None:
    """Tests discovering all supported files with default exclusions."""
    processor = FileProcessor()
    files = list(processor.discover_files(str(temp_repo)))

    assert str(temp_repo / "src" / "main.py") in files
    assert str(temp_repo / "src" / "utils.js") in files
    assert str(temp_repo / "docs" / "guide.md") in files

    # Check that excluded files are not present
    assert str(temp_repo / "data" / "db.sqlite") not in files
    assert str(temp_repo / ".git" / "config") not in files
    assert str(temp_repo / "__pycache__" / "cache.pyc") not in files


@pytest.mark.unit
def test_discover_files_with_include_dirs(temp_repo: Path) -> None:
    """Tests discovering files only from specified include directories."""
    processor = FileProcessor()
    files = list(processor.discover_files(str(temp_repo), include_dirs=["src"]))

    assert len(files) == 2
    assert str(temp_repo / "src" / "main.py") in files
    assert str(temp_repo / "src" / "utils.js") in files
    assert str(temp_repo / "docs" / "guide.md") not in files


@pytest.mark.unit
def test_discover_files_with_custom_exclusions(temp_repo: Path) -> None:
    """Tests discovering files with custom exclusion patterns."""
    processor = FileProcessor(exclude_patterns=["**/*.js"])
    files = list(processor.discover_files(str(temp_repo)))

    assert str(temp_repo / "src" / "main.py") in files
    assert str(temp_repo / "docs" / "guide.md") in files
    assert str(temp_repo / "src" / "utils.js") not in files


@pytest.mark.unit
def test_read_files(temp_repo: Path) -> None:
    """Tests reading multiple files into a dictionary."""
    processor = FileProcessor()
    contents = processor.read_files(str(temp_repo), include_dirs=["src"])

    assert len(contents) == 2
    assert contents[str(temp_repo / "src" / "main.py")] == "print('hello')"
    assert contents[str(temp_repo / "src" / "utils.js")] == "console.log('hello');"


@pytest.mark.unit
def test_read_file_not_found() -> None:
    """Tests that reading a non-existent file returns None."""
    processor = FileProcessor()
    assert processor.read_file("non_existent_file.py") is None
