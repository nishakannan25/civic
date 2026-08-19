@echo off
echo Packaging Civic AI Phase 3 Final into a clean Zip file...
cd /d "%~dp0"
if exist civic-ai\backend\.venv\Scripts\python.exe (
    civic-ai\backend\.venv\Scripts\python.exe create_zip.py
) else if exist backend\.venv\Scripts\python.exe (
    backend\.venv\Scripts\python.exe create_zip.py
) else (
    py create_zip.py || python create_zip.py
)
pause
