@echo off
setlocal
title HeinZ Command Hub
set "DIST_EXE=%~dp0..\dist\HeinZ\HeinZ.exe"
set "DL_EXE=%USERPROFILE%\Downloads\HeinZ\HeinZ\HeinZ.exe"
set "PORTABLE_ZIP=%~dp0..\release\HeinZ-Portable.zip"

if not exist "%DIST_EXE%" if exist "%PORTABLE_ZIP%" (
    echo Extracting standalone HeinZ bundle on first run...
    if not exist "%~dp0..\dist" mkdir "%~dp0..\dist"
    tar -xf "%PORTABLE_ZIP%" -C "%~dp0..\dist" 2>nul
    if not exist "%DIST_EXE%" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%PORTABLE_ZIP%', '%~dp0..\dist', $true)"
    )
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%~dp0..\dist\HeinZ' -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue" >nul 2>&1
)

if exist "%DIST_EXE%" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Item '%DIST_EXE%' -Stream 'Zone.Identifier' -ErrorAction SilentlyContinue) { Get-ChildItem '%~dp0..\dist\HeinZ' -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue }" >nul 2>&1
    start "" "%DIST_EXE%"
) else if exist "%DL_EXE%" (
    start "" "%DL_EXE%"
) else if exist "%~dp0heinzhubweb.py" (
    start "" pythonw "%~dp0heinzhubweb.py"
) else if exist "%~dp0HeinZ Control Hub.py" (
    start "" pythonw "%~dp0HeinZ Control Hub.py"
) else (
    start "" pythonw "%~dp0app.py"
)
exit /b 0
