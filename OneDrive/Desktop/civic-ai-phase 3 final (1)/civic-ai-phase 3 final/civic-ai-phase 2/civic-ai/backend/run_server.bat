@echo off
echo Starting Civic AI Backend...
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m pip install --quiet email-validator
    .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
)
pause
