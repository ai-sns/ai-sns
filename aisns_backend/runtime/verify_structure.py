# -*- coding: utf-8 -*-
"""
Backend Structure Verification Script

Verifies that all backend files are present and have the expected structure.
"""

import os
from pathlib import Path

# Expected files
EXPECTED_FILES = {
    "config": [
        "__init__.py",
        "settings.py",
        "database.py"
    ],
    "core": [
        "__init__.py",
        "dependencies.py"
    ],
    "shared": [
        "__init__.py",
        "websocket_manager.py",
        "utils.py"
    ],
    "root": [
        "__init__.py",
        "README.md",
        "IMPLEMENTATION_SUMMARY.md",
        "QUICK_REFERENCE.md",
        "test_backend.py"
    ]
}

def check_files():
    """Check if all expected files exist"""
    backend_dir = Path(__file__).parent
    missing = []
    present = []

    # Check subdirectories
    for subdir, files in EXPECTED_FILES.items():
        if subdir == "root":
            check_dir = backend_dir
            prefix = "runtime/"
        else:
            check_dir = backend_dir / subdir
            prefix = f"runtime/{subdir}/"

        for filename in files:
            filepath = check_dir / filename
            if filepath.exists():
                present.append(prefix + filename)
            else:
                missing.append(prefix + filename)

    return present, missing


def print_summary():
    """Print summary of backend structure"""
    print("\n" + "=" * 70)
    print("Backend Structure Verification")
    print("=" * 70 + "\n")

    present, missing = check_files()

    if missing:
        print("❌ MISSING FILES:")
        for file in missing:
            print(f"   - {file}")
        print()

    print(f"✓ Found {len(present)} files:")
    print()

    # Group by directory
    by_dir = {}
    for file in present:
        parts = file.split("/")
        dir_name = parts[1] if len(parts) > 2 else "root"
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(parts[-1])

    for dir_name in ["root", "config", "core", "shared"]:
        if dir_name in by_dir:
            print(f"  runtime/{dir_name if dir_name != 'root' else ''}:")
            for filename in sorted(by_dir[dir_name]):
                print(f"    ✓ {filename}")
            print()

    # Calculate total lines
    total_lines = 0
    backend_dir = Path(__file__).parent

    py_files = [
        "config/settings.py",
        "config/database.py",
        "core/dependencies.py",
        "shared/websocket_manager.py",
        "shared/utils.py"
    ]

    print("Code Statistics:")
    for py_file in py_files:
        filepath = backend_dir / py_file
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  {py_file:40} {lines:4} lines")

    print(f"\n  {'Total:':<40} {total_lines:4} lines")
    print()

    if missing:
        print("=" * 70)
        print(f"Status: INCOMPLETE - {len(missing)} file(s) missing")
        print("=" * 70 + "\n")
        return False
    else:
        print("=" * 70)
        print("Status: COMPLETE - All files present")
        print("=" * 70 + "\n")
        return True


if __name__ == "__main__":
    import sys
    success = print_summary()
    sys.exit(0 if success else 1)
