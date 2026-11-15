@echo off
rem Double-click this on the PC with the GPU. It starts the dashboard with the local AI,
rem opens it in the browser, and prints the address to open on the Legion Go.
rem Leave this window open while you use the dashboard. Close it to stop.
title Flame in Freefall dashboard
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py server\serve.py --lan --open
) else (
  python server\serve.py --lan --open
)
echo.
echo The dashboard has stopped. If it never started, install Python from python.org and try again.
pause
