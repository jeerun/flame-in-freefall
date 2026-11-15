@echo off
rem Start the PC dashboard on loopback. For private LAN setup see docs\legion-go-setup.md.
setlocal
title Flame in Freefall dashboard
pushd "%~dp0" || exit /b 1
where py >nul 2>nul
if errorlevel 1 (
  python server\serve.py --open
) else (
  py server\serve.py --open
)
set "DASHBOARD_EXIT=%errorlevel%"
popd
echo.
echo The dashboard has stopped.
pause
exit /b %DASHBOARD_EXIT%
