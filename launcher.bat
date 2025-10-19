@echo off
title Password Keeper - Portable
cls

echo.
echo ===============================================
echo    Password Keeper - Portable Edition
echo ===============================================
echo.
echo Starting Password Keeper...
echo Data will be stored in this folder.
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if the executable exists
if not exist "PasswordKeeper.exe" (
    echo ERROR: PasswordKeeper.exe not found!
    echo Make sure this batch file is in the same folder as PasswordKeeper.exe
    echo.
    pause
    exit /b 1
)

REM Check if portable.txt exists
if not exist "portable.txt" (
    echo WARNING: portable.txt not found!
    echo Creating portable mode marker...
    echo PORTABLE MODE ENABLED > portable.txt
)

REM Create data directory if it doesn't exist
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Start the application
echo Launching Password Keeper...
start "" "PasswordKeeper.exe"

REM Check if application started successfully
timeout /t 2 /nobreak >nul
tasklist /fi "imagename eq PasswordKeeper.exe" 2>nul | find /i "PasswordKeeper.exe" >nul
if %errorlevel% equ 0 (
    echo.
    echo Password Keeper started successfully!
    echo You can close this window.
) else (
    echo.
    echo WARNING: Password Keeper may not have started correctly.
    echo If you encounter issues:
    echo  1. Make sure Windows is up to date
    echo  2. Try running as administrator
    echo  3. Check that antivirus isn't blocking the app
    echo.
    pause
)

REM Optional: Keep window open for debugging
REM pause