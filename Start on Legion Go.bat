@echo off
rem Start the handheld dashboard. Python reads and validates the optional saved PC address.
setlocal
title Flame in Freefall on the handheld
pushd "%~dp0" || exit /b 1
where py >nul 2>nul
if errorlevel 1 (
  python server\serve.py --open --model gemma4:e2b --name "the Legion Go itself" --handheld-peer
) else (
  py server\serve.py --open --model gemma4:e2b --name "the Legion Go itself" --handheld-peer
)
set "DASHBOARD_EXIT=%errorlevel%"
popd
echo.
echo The dashboard has stopped.
pause
exit /b %DASHBOARD_EXIT%
