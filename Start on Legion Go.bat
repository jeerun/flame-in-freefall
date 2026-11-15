@echo off
rem Double-click this ON THE LEGION GO (or any second machine) when it has its own small AI model.
rem It runs the dashboard on the handheld itself and links it to the big PC:
rem   - while the PC answers, Ember thinks on the PC (the big model)
rem   - when the PC is out of reach, Ember answers from the model on this handheld
rem Needs, on the handheld, once:  Python (python.org), Ollama (ollama.com), and:  ollama pull gemma4:e2b
rem If you only want to use the PC's AI, you do not need this file: open the address the PC prints, in the browser.
title Flame in Freefall on the handheld
cd /d "%~dp0"
set "PCFILE=%~dp0pc-address.txt"
set "PC="
if exist "%PCFILE%" set /p PC=<"%PCFILE%"
if not defined PC (
  echo On the PC, "Start dashboard.bat" prints a line like:  On the Legion Go ^(same Wi-Fi^): http://192.168.1.23:8000
  set /p PC=Type that address here ^(or press Enter to run without the PC^):
)
if defined PC (
  >"%PCFILE%" echo %PC%
  echo Linking to the PC at %PC% . To change it, delete pc-address.txt.
  set "PEER=--peer %PC%"
) else (
  set "PEER="
)
where py >nul 2>nul
if %errorlevel%==0 (
  py server\serve.py --open --model gemma4:e2b --name "the Legion Go itself" %PEER%
) else (
  python server\serve.py --open --model gemma4:e2b --name "the Legion Go itself" %PEER%
)
echo.
echo The dashboard has stopped. If it never started, install Python from python.org and try again.
pause
