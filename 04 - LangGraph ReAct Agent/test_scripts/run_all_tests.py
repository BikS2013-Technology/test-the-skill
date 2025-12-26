"""
Run All Tests for LangGraph ReAct Agent Guide

This script runs all test files in sequence and provides a summary.
"""

import sys
import subprocess
from pathlib import Path


def run_test(test_file: str) -> bool:
    """Run a single test file and return True if it passed."""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print('='*70)

    result = subprocess.run(
        [sys.executable, test_file],
        cwd=str(Path(test_file).parent.parent),
        capture_output=False
    )

    return result.returncode == 0


def main():
    """Run all tests and provide summary."""
    test_dir = Path(__file__).parent

    # List of all test files in order
    test_files = [
        "test_01_basic_usage.py",
        "test_02_with_system_prompt.py",
        "test_03_with_memory.py",
        "test_04_custom_react_graph.py",
        "test_05_tavily_configurations.py",
        "test_06_custom_tools.py",
        "test_07_streaming.py",
        "test_08_async_streaming.py",
        "test_09_dynamic_prompts.py",
        "test_10_graph_visualization.py",
        "test_11_simple_research_agent.py",
        "test_12_interactive_chat.py",
        "test_13_extended_state_graph.py",
        "test_14_best_practices.py",
    ]

    results = {}

    print("="*70)
    print("LangGraph ReAct Agent Guide - Test Suite")
    print("="*70)

    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            passed = run_test(str(test_path))
            results[test_file] = "PASSED" if passed else "FAILED"
        else:
            results[test_file] = "NOT FOUND"

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed_count = 0
    failed_count = 0

    for test_file, status in results.items():
        status_icon = "[OK]" if status == "PASSED" else "[FAIL]"
        print(f"  {status_icon} {test_file}: {status}")
        if status == "PASSED":
            passed_count += 1
        else:
            failed_count += 1

    print("-"*70)
    print(f"Total: {passed_count} passed, {failed_count} failed")
    print("="*70)

    return failed_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
