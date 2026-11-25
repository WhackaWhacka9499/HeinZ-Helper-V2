@echo off
title Last Z Auto-Engine Status
echo - Last Z auto-engine watcher status and telemetry -
echo.
python "%~dp0..\telemetry\check v7 status.py"
echo.
if exist "%~dp0..\daemon\lastz_auto_engine.log" (
    echo --- Recent Daemon Log ---
    powershell -Command "Get-Content '%~dp0..\daemon\lastz_auto_engine.log' -Tail 15"
)
echo.
echo ---------------------------------------------------
pause
