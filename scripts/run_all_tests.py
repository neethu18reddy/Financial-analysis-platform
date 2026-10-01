"""Automated Test Runner for AI Financial Decision Intelligence Platform."""

import subprocess
import sys
import time

# Ensure proper stdout encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_command(command: str, description: str, cwd=None) -> bool:
    """Executes a subprocess command and prints formatted results."""
    print(f"\n========================================================")
    print(f"[*] RUNNING: {description}")
    print(f"[*] COMMAND: {command}")
    print(f"========================================================")
    start = time.perf_counter()
    result = subprocess.run(command, shell=True, cwd=cwd)
    duration = time.perf_counter() - start
    if result.returncode == 0:
        print(f"[PASS] {description} ({duration:.2f}s)")
        return True
    else:
        print(f"[FAIL] {description} (Exit Code: {result.returncode})")
        return False


def main():
    print("\n========================================================")
    print("PHASE 0 TEST SUITE: BACKEND, DATABASE, AND FRONTEND")
    print("========================================================")

    results = []

    # 1. Backend Pytest suite
    results.append(
        run_command(
            ".venv\\Scripts\\pytest tests/backend -v",
            "Backend Unit & Integration Tests (FastAPI, DB, Health, Errors)",
        )
    )

    # 2. Frontend TypeScript & Build verification
    results.append(
        run_command(
            "npm run build",
            "Frontend TypeScript Compile & Production Bundle Build",
            cwd="frontend",
        )
    )

    print("\n========================================================")
    print("TEST SUITE SUMMARY")
    print("========================================================")
    total = len(results)
    passed = sum(1 for r in results if r)
    print(f"Total Suites: {total} | Passed: {passed} | Failed: {total - passed}")

    if all(results):
        print("\n[ALL PASS] ALL PHASE 0 TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n[FAIL] SOME TESTS FAILED. PLEASE FIX ISSUES BEFORE CONTINUING.")
        sys.exit(1)


if __name__ == "__main__":
    main()
