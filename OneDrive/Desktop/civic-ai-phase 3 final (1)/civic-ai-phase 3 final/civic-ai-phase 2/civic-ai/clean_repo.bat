@echo off
echo ===================================================
echo  Civic AI - Repository Cleaning Utility
echo ===================================================
echo Removing generated caches, virtual environments, and temporary files...

cd /d "%~dp0"

:: Remove Python caches
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo Removing: %%d
        rd /s /q "%%d" 2>nul
    )
)

:: Remove pytest caches
for /d /r . %%d in (.pytest_cache) do (
    if exist "%%d" (
        echo Removing: %%d
        rd /s /q "%%d" 2>nul
    )
)

:: Remove Flutter build & cache directories
if exist "mobile\.dart_tool" (
    echo Removing: mobile\.dart_tool
    rd /s /q "mobile\.dart_tool" 2>nul
)
if exist "mobile\build" (
    echo Removing: mobile\build
    rd /s /q "mobile\build" 2>nul
)

:: Remove virtual environment if requested
if exist "backend\.venv" (
    echo Removing: backend\.venv
    rd /s /q "backend\.venv" 2>nul
)

:: Remove temporary databases or logs
if exist "backend\*.sqlite3" del /q /f "backend\*.sqlite3" 2>nul
if exist "backend\*.db" del /q /f "backend\*.db" 2>nul
if exist "*.log" del /q /f "*.log" 2>nul
if exist "backend\*.log" del /q /f "backend\*.log" 2>nul

echo.
echo ===================================================
echo  Repository is clean and ready for sharing!
echo ===================================================
pause
