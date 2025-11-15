"""Validation script to ensure examples run correctly.

This script executes all example files and validates they complete without errors.
Useful for CI/CD validation and pre-release testing.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple


def run_example(example_path: Path) -> Tuple[str, bool, str]:
    """Run an example script and return its status.
    
    Args:
        example_path: Path to the example Python file
        
    Returns:
        Tuple of (example_name, success, error_message)
    """
    example_name = example_path.stem
    
    try:
        # Load the example module
        spec = importlib.util.spec_from_file_location(example_name, example_path)
        if spec is None or spec.loader is None:
            return (example_name, False, "Failed to load module spec")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[example_name] = module
        
        # Execute the example
        spec.loader.exec_module(module)
        
        # Run main function if it exists
        if hasattr(module, "main"):
            module.main()
        
        return (example_name, True, "")
        
    except Exception as e:
        return (example_name, False, str(e))
    finally:
        # Clean up
        if example_name in sys.modules:
            del sys.modules[example_name]


def main() -> int:
    """Run all examples and report results.
    
    Returns:
        Exit code: 0 if all pass, 1 if any fail
    """
    print("=" * 70)
    print("Example Validation Suite")
    print("=" * 70)
    print()

    # Find all example files
    examples_dir = Path(__file__).parent
    example_files = sorted(examples_dir.glob("*.py"))
    example_files = [f for f in example_files 
                     if f.name not in ["__init__.py", "validate_examples.py"]]
    
    if not example_files:
        print("✗ No example files found!")
        return 1
    
    print(f"Found {len(example_files)} example(s) to validate:")
    for example_file in example_files:
        print(f"  • {example_file.name}")
    print()

    # Run each example
    results: List[Tuple[str, bool, str]] = []
    
    for example_file in example_files:
        print("-" * 70)
        print(f"Running: {example_file.name}")
        print("-" * 70)
        
        name, success, error = run_example(example_file)
        results.append((name, success, error))
        
        if success:
            print(f"\n✓ {name} completed successfully")
        else:
            print(f"\n✗ {name} failed: {error}")
        print()

    # Print summary
    print("=" * 70)
    print("Validation Summary")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"Total Examples: {len(results)}")
    print(f"Passed:         {passed} ✓")
    print(f"Failed:         {failed} {'✗' if failed > 0 else ''}")
    print()
    
    if failed > 0:
        print("Failed Examples:")
        for name, success, error in results:
            if not success:
                print(f"  ✗ {name}: {error}")
        print()
    
    # Return appropriate exit code
    if failed > 0:
        print("=" * 70)
        print("VALIDATION FAILED")
        print("=" * 70)
        return 1
    else:
        print("=" * 70)
        print("ALL EXAMPLES PASSED")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
