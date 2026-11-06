
@echo off
cd /d "%~dp0task2_local_rag"

if not exist .venv\Scripts\python.exe (
    echo First run: creating Python virtual environment...
    python -m venv .venv

    if errorlevel 1 (
        echo Failed to create virtual environment. Check Python installation.
        pause
        exit /b 1
    )

    echo Upgrading pip...
    .venv\Scripts\python.exe -m pip install --upgrade pip

    echo Installing Task 2 dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt

    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
)

echo Starting Task 2 - Local RAG Chatbot...
start "" http://127.0.0.1:8001

.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001

pause
