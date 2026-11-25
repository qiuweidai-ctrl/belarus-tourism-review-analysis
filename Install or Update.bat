@echo off
setlocal
title Belarus Tourism - Update
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Manage.ps1" -Action Update
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
