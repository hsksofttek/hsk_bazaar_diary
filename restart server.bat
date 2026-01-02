@echo off
setlocal
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Activate venv
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo Virtual env not found. Please create .venv first.
    exit /b 1
)

REM Run the app; set env as needed
set FLASK_DEBUG=1
set FLASK_RUN_HOST=127.0.0.1
set FLASK_RUN_PORT=5000
REM set ENABLE_LEGACY_ROUTES=true

python run.py
endlocal
