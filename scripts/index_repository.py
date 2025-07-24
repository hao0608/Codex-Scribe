"""
This script provides a command-line interface to index a local code repository.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.application.use_cases.index_repository import IndexRepositoryUseCase
from src.infrastructure.database.chroma_client import ChromaDBClient
from src.infrastructure.file_processor import FileProcessor
from src.infrastructure.llm.openai_client import OpenAIClient
from src.infrastructure.text_splitter import CodeTextSplitter


def main() -> None:
    """
    Main function to parse arguments and run the indexing use case.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Index a local code repository.")
    parser.add_argument(
        "repo_path",
        type=str,
        help="The local path to the code repository to be indexed.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.repo_path):
        print(f"Error: Directory not found at {args.repo_path}")
        sys.exit(1)

    try:
        # --- Dependency Injection ---
        # In a real application, this would be handled by a DI container.
        file_processor = FileProcessor()
        text_splitter = CodeTextSplitter()
        openai_client = OpenAIClient()
        chroma_client = ChromaDBClient()

        index_use_case = IndexRepositoryUseCase(
            file_processor=file_processor,
            text_splitter=text_splitter,
            embedding_service=openai_client,
            code_repository=chroma_client,
        )
        # --- End of Dependency Injection ---

        index_use_case.execute(args.repo_path)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
