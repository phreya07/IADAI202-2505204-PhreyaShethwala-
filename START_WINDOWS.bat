@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.13 -m venv .venv
  if errorlevel 1 (
    echo Please install 64-bit Python 3.13, then run this file again.
    pause
    exit /b 1
  )
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection and read README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py
pause
