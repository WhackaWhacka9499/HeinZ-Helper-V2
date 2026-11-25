@echo off
setlocal
title HeinZ Command Hub - Clean-PC Diagnostics
set "HERE=%~dp0"
set "EXE=%HERE%HeinZ.exe"
if not exist "%EXE%" (
    if exist "%HERE%..\dist\HeinZ\HeinZ.exe" set "EXE=%HERE%..\dist\HeinZ\HeinZ.exe"
)

if not exist "%EXE%" (
    echo [ERROR] HeinZ.exe was not found next to this script.
    pause
    exit /b 1
)

echo Running HeinZ Heavy Diagnostics (unblocking files first)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%HERE%' -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue" >nul 2>&1

start "" /wait "%EXE%" --diagnose
set "RC=%ERRORLEVEL%"

echo.
echo Diagnostics finished (exit code %RC%).
echo A privacy-redacted report (HeinZ_Diagnostic_Report_*.txt) has been saved to your Desktop.
echo Check Desktop if the popup already closed.
pause
exit /b %RC%
