@echo off
setlocal enabledelayedexpansion

set "PY="

REM Check if python command works
python --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PY=python"
)

REM If not, check known Windows user path
if not defined PY (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    ) else if exist "C:\Python313\python.exe" (
        set "PY=C:\Python313\python.exe"
    ) else if exist "%ProgramFiles%\Python313\python.exe" (
        set "PY=%ProgramFiles%\Python313\python.exe"
    )
)

if not defined PY (
    echo [!] Python executable not found.
    echo Please ensure Python 3.10+ is installed.
    exit /b 1
)

"%PY%" "%~dp0main.py" %*
exit /b %ERRORLEVEL%
