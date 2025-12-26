"""
Run All Tests Script
Executes all LangChain Fundamentals test scripts in sequence.
"""

import subprocess
import sys
import os

# Get the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# List of test scripts in order
TEST_SCRIPTS = [
    "01_llm_connection.py",
    "02_messages_conversations.py",
    "03_simple_chat_application.py",
    "04_streaming_responses.py",
    "05_prompt_templates.py",
    "06_chains_runnables_lcel.py",
    "07_structured_output.py",
    "08_tool_integration.py",
    "09_complete_examples.py",
    "10_best_practices.py",
]


def run_test(script_name):
    """Run a single test script and return the result."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70)

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False,
        text=True
    )

    return result.returncode == 0


def main():
    print("=" * 70)
    print("LANGCHAIN FUNDAMENTALS - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    results = []
    for script in TEST_SCRIPTS:
        try:
            success = run_test(script)
            results.append((script, "PASSED" if success else "FAILED"))
        except Exception as e:
            results.append((script, f"ERROR: {e}"))

    print("\n" + "=" * 70)
    print("FINAL SUMMARY - ALL TESTS")
    print("=" * 70)
    passed = 0
    failed = 0
    for script, result in results:
        status = "PASSED" if "PASSED" in result else "FAILED/ERROR"
        if "PASSED" in result:
            passed += 1
        else:
            failed += 1
        print(f"  {script}: {result}")

    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} test scripts")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
