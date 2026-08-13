@echo off
setlocal
cd /d "%~dp0"
title RealTime local faster-whisper

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found.
  echo Install Python 3.10 or newer from https://www.python.org/downloads/windows/
  echo During installation, enable "Add python.exe to PATH", then run this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating the local Python environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
)

echo Installing or updating faster-whisper dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements-local-whisper.txt
if errorlevel 1 goto :failed

echo.
echo Starting local faster-whisper at http://127.0.0.1:8000
echo Keep this window open while transcribing. Press Ctrl+C to stop.
echo The model is downloaded automatically on the first transcription.
echo.
".venv\Scripts\python.exe" local_whisper_server.py --device cpu --compute-type int8
if errorlevel 1 goto :failed
exit /b 0

:failed
echo.
echo [ERROR] Setup or startup failed. Review the message above.
pause
exit /b 1
