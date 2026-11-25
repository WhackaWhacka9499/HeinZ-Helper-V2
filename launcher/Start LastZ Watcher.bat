@echo off
setlocal
title Launch Last Z Enhanced
echo Starting Last Z Auto-Engine Watcher Daemon...
set "DIST_EXE=%~dp0..\dist\HeinZ\HeinZ.exe"
if exist "%DIST_EXE%" (
    start "" "%DIST_EXE%" --run-script "%~dp0..\dist\HeinZ\_internal\daemon\lastz auto engine daemon.py"
) else (
    start "" pythonw "%~dp0..\daemon\lastz auto engine daemon.py"
)
echo Watcher active! You can launch Survival.exe now.
timeout /t 2 >nul
exit /b 0
