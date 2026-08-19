#!/usr/bin/env python3
"""
Civic AI - Repository Sanitization & Cleanup Utility
Cleans all caches, build directories, logs, and virtual environments
to prepare the repository for sharing with teammates.
"""
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

DIRS_TO_REMOVE = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    ".dart_tool",
    "build",
    ".coverage",
    "htmlcov",
]

FILES_TO_REMOVE_EXT = [
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".sqlite3",
    ".db",
]

def clean_repository():
    print(f"[*] Sanitizing repository at: {ROOT_DIR}")
    cleaned_dirs = 0
    cleaned_files = 0

    # 1. Walk and remove directories
    for root, dirs, files in os.walk(ROOT_DIR, topdown=False):
        for dir_name in dirs:
            if dir_name in DIRS_TO_REMOVE:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path, ignore_errors=True)
                    print(f"[-] Removed directory: {os.path.relpath(dir_path, ROOT_DIR)}")
                    cleaned_dirs += 1
                except Exception as e:
                    print(f"[!] Could not remove {dir_path}: {e}")

        # 2. Remove cache and temporary files
        for file_name in files:
            if any(file_name.endswith(ext) for ext in FILES_TO_REMOVE_EXT):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    print(f"[-] Removed file: {os.path.relpath(file_path, ROOT_DIR)}")
                    cleaned_files += 1
                except Exception as e:
                    print(f"[!] Could not remove {file_path}: {e}")

    print("\n" + "=" * 60)
    print(f"[✓] Sanitization complete: {cleaned_dirs} directories and {cleaned_files} files removed.")
    print("[✓] Ready for sharing with teammates!")
    print("=" * 60)

if __name__ == "__main__":
    clean_repository()
