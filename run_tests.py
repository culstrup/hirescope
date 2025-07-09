#!/usr/bin/env python3
"""
Quick test runner to verify testing setup
Run with: python run_tests.py
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print("=" * 60)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)

    return result.returncode == 0


def main():
    """Run basic tests to verify setup"""
    print("🧪 HireScope Testing Setup Verification")
    print("=" * 60)

    # Check if we're in virtual environment
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Warning: Not in a virtual environment!")
        print("   Run: source venv/bin/activate")

    # Check if test dependencies are installed
    try:
        import pytest  # noqa: F401
        import pytest_cov  # noqa: F401

        print("✅ Test dependencies installed")
    except ImportError as e:
        print(f"❌ Missing test dependencies: {e}")
        print("   Run: pip install -r requirements-dev.txt")
        return 1

    # Run tests
    all_passed = True

    # 1. Unit tests
    if not run_command(
        "pytest tests/unit/test_document_processor.py -v",
        "Unit Tests for DocumentProcessor",
    ):
        all_passed = False

    # 2. Linting
    if not run_command("ruff check hirescope/document_processor.py", "Ruff Linting"):
        all_passed = False

    # 3. Type checking
    if not run_command(
        "mypy hirescope/document_processor.py --ignore-missing-imports",
        "MyPy Type Checking",
    ):
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Testing infrastructure is working correctly.")
        print("\nNext steps:")
        print("1. Run full test suite: make test-all")
        print("2. Set up pre-commit: pre-commit install")
        print("3. Run pre-commit on all files: make pre-commit")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
