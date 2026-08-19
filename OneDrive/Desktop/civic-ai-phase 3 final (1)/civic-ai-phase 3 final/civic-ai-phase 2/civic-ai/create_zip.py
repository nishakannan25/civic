#!/usr/bin/env python3
"""
Civic AI - Phase 3 Final Zip Archive Generator
Creates a clean, sanitized zip file of the repository excluding caches, .venv, and build artifacts.
"""
import os
import zipfile
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if (CURRENT_DIR / "civic-ai").is_dir():
    REPO_DIR = CURRENT_DIR / "civic-ai"
    OUTPUT_ZIP = CURRENT_DIR / "civic-ai-phase3-final.zip"
else:
    REPO_DIR = CURRENT_DIR
    OUTPUT_ZIP = CURRENT_DIR.parent / "civic-ai-phase3-final.zip"

EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".dart_tool",
    "build",
    ".git",
    ".idea",
    ".vscode",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".sqlite3",
    ".db",
}

def create_sanitized_zip():
    print(f"[*] Packaging repository: {REPO_DIR}")
    print(f"[*] Destination: {OUTPUT_ZIP}")
    
    file_count = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(REPO_DIR):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

            for file in files:
                # Skip excluded file extensions and temp zips/scripts
                if any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue
                if file.startswith("civic-ai-phase") or file.endswith(".zip") or file in {"create_zip.py", "create_zip.bat"}:
                    continue

                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(REPO_DIR)
                
                # Prepend top-level 'civic-ai/' folder in zip
                archive_name = Path("civic-ai") / rel_path
                zipf.write(abs_path, arcname=str(archive_name))
                file_count += 1

    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print("=" * 60)
    print(f"[✓] Zip created successfully!")
    print(f"[✓] Location: {OUTPUT_ZIP}")
    print(f"[✓] Files included: {file_count}")
    print(f"[✓] Archive size: {zip_size_mb:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    create_sanitized_zip()
