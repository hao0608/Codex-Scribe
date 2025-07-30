"""
This script provides a command-line interface to index a local code repository.
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.application.use_cases.index_repository import IndexRepositoryUseCase
from src.infrastructure.database.chroma_client import ChromaDBClient
from src.infrastructure.database.graph_db import Neo4jService
from src.infrastructure.file_processor import FileProcessor
from src.infrastructure.llm.openai_client import AsyncOpenAIClient
from src.infrastructure.parser.code_parser import CodeParser
from src.infrastructure.text_splitter import CodeTextSplitter


async def main() -> None:
    """
    Main async function to parse arguments and run the indexing use case.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Index a local code repository.")
    parser.add_argument(
        "repo_path",
        type=str,
        help="The local path to the code repository to be indexed.",
    )
    parser.add_argument(
        "--include-dirs",
        nargs="+",
        help="A list of specific directories to include in the indexing.",
    )
    parser.add_argument(
        "--exclude-patterns",
        nargs="+",
        help="A list of glob patterns to exclude from indexing.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.repo_path):
        print(f"Error: Directory not found at {args.repo_path}")
        sys.exit(1)

    try:
        # --- Dependency Injection ---
        file_processor = FileProcessor(exclude_patterns=args.exclude_patterns)
        text_splitter = CodeTextSplitter()
        openai_client = AsyncOpenAIClient()
        chroma_client = ChromaDBClient()
        code_parser = CodeParser()

        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")

        graph_repository = Neo4jService(
            uri=neo4j_uri, user=neo4j_user, password=neo4j_password
        )

        index_use_case = IndexRepositoryUseCase(
            file_processor=file_processor,
            text_splitter=text_splitter,
            embedding_client=openai_client,
            code_repository=chroma_client,
            graph_repository=graph_repository,
            code_parser=code_parser,
        )
        # --- End of Dependency Injection ---

        await index_use_case.execute(args.repo_path, args.include_dirs)

        graph_repository.close()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
