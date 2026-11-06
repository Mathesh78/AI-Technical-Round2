@echo off
cd /d "%~dp0task1_knowledge_hub"
if not exist .venv\Scripts\python.exe (
  echo First run: creating Python virtual environment and installing dependencies...
  python -m venv .venv
  if errorlevel 1 (echo Install Python 3.11 and enable py launcher & pause & exit /b 1)
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (echo Failed to install requirements & pause & exit /b 1)
)
start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
