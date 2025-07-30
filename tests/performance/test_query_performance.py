"""
Performance tests for the query pipeline.
"""

import cProfile
import os
import pstats
import sys
import time

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.application.use_cases.answer_question import AnswerQuestionUseCase
from src.application.use_cases.graph_query import GraphQueryUseCase
from src.infrastructure.database.chroma_client import ChromaDBClient
from src.infrastructure.database.graph_db import Neo4jService
from src.infrastructure.llm.openai_client import OpenAIClient


def run_query_performance_test(use_case: AnswerQuestionUseCase, query: str) -> float:
    """
    Runs a query and measures its performance.
    """
    print(f"--- Running performance test for query: '{query}' ---")

    profiler = cProfile.Profile()

    start_time = time.time()

    # Run the query
    profiler.enable()
    response = use_case.execute(query)
    profiler.disable()

    end_time = time.time()

    total_time = end_time - start_time
    print(f"Total query time: {total_time:.2f} seconds")
    print(f"Response: {response}")

    # Print profiling stats
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)

    return total_time


if __name__ == "__main__":
    # Setup dependencies
    embedding_service = OpenAIClient()
    code_repository = ChromaDBClient()
    llm_client = OpenAIClient()
    neo4j_service = Neo4jService("bolt://localhost:7687", "neo4j", "password123")
    graph_query_use_case = GraphQueryUseCase(neo4j_service)

    answer_question_use_case = AnswerQuestionUseCase(
        embedding_service=embedding_service,
        code_repository=code_repository,
        llm_client=llm_client,
        graph_query_use_case=graph_query_use_case,
    )

    # Test cases
    vector_search_query = "How does the CodeParser work?"
    graph_query_callers = 'Who calls the "parse" function?'
    graph_query_methods = 'What methods are in the "CodeParser" class?'

    print("--- Starting Query Performance Tests ---")

    run_query_performance_test(answer_question_use_case, vector_search_query)
    run_query_performance_test(answer_question_use_case, graph_query_callers)
    run_query_performance_test(answer_question_use_case, graph_query_methods)

    print("--- Query Performance Tests Finished ---")

    neo4j_service.close()
