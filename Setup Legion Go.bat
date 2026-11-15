@echo off
rem Run this ONCE on the Legion Go (double-click), with internet. It installs what the handheld needs to run
rem the dashboard with its own small AI model:
rem   1. Python          (runs the small local server; about 30 MB)
rem   2. Ollama          (runs the AI model on this device)
rem   3. gemma4:e2b      (the small AI model; about 4.3 GB to download)
rem It uses winget, the installer that comes with Windows 11. winget shows each program's licence and asks
rem you to agree: answer Y yourself. Nothing is installed without that.
rem Afterwards double-click "Start on Legion Go.bat".
rem
rem You do NOT need any of this to use the dashboard with the PC's AI: for that, open the address the PC
rem prints, in Edge on the Legion Go.
title Flame in Freefall: set up the handheld
cd /d "%~dp0"
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

where winget >nul 2>nul
if errorlevel 1 (
  echo winget was not found. Install "App Installer" from the Microsoft Store, then run this again.
  goto done
)

echo.
echo Step 1 of 3: Python
where py >nul 2>nul
if errorlevel 1 (
  winget install --id Python.Python.3.13 --exact
) else (
  echo   already installed
)

echo.
echo Step 2 of 3: Ollama
if exist "%OLLAMA%" (
  echo   already installed
) else (
  winget install --id Ollama.Ollama --exact
)
if not exist "%OLLAMA%" (
  echo   Ollama is not where it is expected: %OLLAMA%
  echo   If you just installed it, close this window and run this file again.
  goto done
)

echo.
echo Step 3 of 3: the small AI model, gemma4:e2b, about 4.3 GB
"%OLLAMA%" list >nul 2>nul
if errorlevel 1 (
  echo   starting Ollama ...
  start "Ollama" /min "%OLLAMA%" serve
  timeout /t 6 /nobreak >nul
)
"%OLLAMA%" pull gemma4:e2b
if errorlevel 1 (
  echo   The model did not download. Check the internet connection and run this file again.
  goto done
)

echo.
echo Models on this device:
"%OLLAMA%" list
echo.
echo Done. Now double-click "Start on Legion Go.bat".
echo If it says Python is missing, close every window once so Windows picks up the new install, and try again.

:done
echo.
pause
