@echo off
setlocal
title PDF QA
cd /d "%~dp0"

rem ---- Settings (keep in sync with backend\config.py) ----
set "LLM_MODEL=qwen2.5:7b"
set "EMBED_MODEL=bge-m3"
rem Where Ollama keeps its models (only used if Start.bat has to start Ollama itself).
rem If your other project stores models in a custom folder, put that folder here.
rem Default = the normal Ollama folder, so models you
rem already downloaded are reused (no internet needed).
rem To keep models inside this project instead, copy the "blobs" and "manifests" folders from
rem %USERPROFILE%\.ollama\models into the "models" folder here, then use:
rem   set "OLLAMA_MODELS=%~dp0models"
set "OLLAMA_MODELS=%USERPROFILE%\.ollama\models"
rem Ollama port. 5005 is the port your existing Ollama already uses, so it is reused if running.
rem (The default 11434 can be blocked by Windows.) Change this number if you get a
rem "forbidden by its access permissions" error.
set "OLLAMA_PORT=5005"
set "OLLAMA_HOST=127.0.0.1:%OLLAMA_PORT%"
set "OLLAMA_URL=http://127.0.0.1:%OLLAMA_PORT%"
set "PY=%~dp0backend\venv\Scripts\python.exe"
set "OLLAMA_LOG=%~dp0logs\ollama_server.log"

rem ---- Check requirements ----
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10+ and tick "Add to PATH".
  pause
  exit /b 1
)
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama was not found. Install it from https://ollama.com/download
  pause
  exit /b 1
)

rem ---- Python environment ----
if not exist "%PY%" (
  echo Creating virtual environment...
  python -m venv backend\venv
  if errorlevel 1 (
    echo Could not create the virtual environment.
    pause
    exit /b 1
  )
)
if not exist "backend\venv\.deps_installed" (
  echo Installing Python packages...
  "%PY%" -m pip install -r backend\requirements.txt
  if errorlevel 1 (
    echo Package installation failed.
    pause
    exit /b 1
  )
  echo ok> backend\venv\.deps_installed
)

rem ---- Make sure Ollama is running ----
ollama list >nul 2>nul
if not errorlevel 1 (
  echo Ollama is already running - using it.
  goto ollama_ready
)

echo Starting Ollama...
start "" /b ollama serve > "%OLLAMA_LOG%" 2>&1

set /a tries=0
:wait_ollama
ollama list >nul 2>nul
if not errorlevel 1 goto ollama_ready
set /a tries+=1
if %tries% GEQ 30 goto ollama_failed
timeout /t 1 >nul
goto wait_ollama

:ollama_failed
echo.
echo Ollama did not start. Its output was:
echo ----------------------------------------
type "%OLLAMA_LOG%"
echo ----------------------------------------
echo If the message above mentions the port, change OLLAMA_PORT at the top of Start.bat.
pause
exit /b 1

:ollama_ready
echo.
echo Installed models:
ollama list
echo.

ollama show %LLM_MODEL% >nul 2>nul
if errorlevel 1 (
  echo Downloading %LLM_MODEL% ...
  ollama pull %LLM_MODEL%
  ollama show %LLM_MODEL% >nul 2>nul
  if errorlevel 1 (
    echo.
    echo WARNING: %LLM_MODEL% is not installed and could not be downloaded.
    echo Check your internet/VPN, or set LLM_MODEL at the top of Start.bat
    echo to one of the models listed above.
    echo.
  )
)
ollama show %EMBED_MODEL% >nul 2>nul
if errorlevel 1 (
  echo Downloading %EMBED_MODEL% ...
  ollama pull %EMBED_MODEL%
  ollama show %EMBED_MODEL% >nul 2>nul
  if errorlevel 1 (
    echo.
    echo NOTE: %EMBED_MODEL% is not available, so the app will use keyword search instead.
    echo.
  )
)

rem ---- Run the app (opens the browser) ----
echo.
echo Starting the app at http://127.0.0.1:8000  (close this window to stop)
cd backend
"%PY%" main.py
pause
