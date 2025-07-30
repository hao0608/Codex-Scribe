"""
Performance tests for the indexing pipeline.
"""

import cProfile
import os
import pstats
import sys
import time

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import subprocess


def run_indexing_performance_test(
    repo_path: str, include_dirs: list[str]
) -> float | None:
    """
    Runs the indexing process and measures its performance.
    """
    print(f"--- Running performance test for: {include_dirs} ---")

    profiler = cProfile.Profile()

    start_time = time.time()

    # Build the command
    command = ["python", "scripts/index_repository.py", repo_path]
    if include_dirs:
        command.append("--include-dirs")
        command.extend(include_dirs)

    # Run the indexing script as a subprocess
    profiler.enable()
    process = subprocess.run(command, capture_output=True, text=True)
    profiler.disable()

    end_time = time.time()

    if process.returncode != 0:
        print(f"Indexing script failed for {include_dirs}:")
        print(process.stderr)
        return None

    total_time = end_time - start_time
    print(f"Total indexing time: {total_time:.2f} seconds")

    # Print profiling stats
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)  # Print top 20 functions by cumulative time

    return total_time


if __name__ == "__main__":
    # Test cases
    small_project = ["src/domain"]
    medium_project = ["src/application", "src/infrastructure", "src/domain"]
    large_project = ["src"]

    print("--- Starting Indexing Performance Tests ---")

    # Small project test
    run_indexing_performance_test(".", small_project)

    # Medium project test
    run_indexing_performance_test(".", medium_project)

    # Large project test
    run_indexing_performance_test(".", large_project)

    print("--- Indexing Performance Tests Finished ---")
