@echo off
echo Running Civic AI Phase 1 Tests...
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m pip install --quiet email-validator
    .venv\Scripts\python.exe run_phase1_tests.py
) else (
    py run_phase1_tests.py
)
pause
