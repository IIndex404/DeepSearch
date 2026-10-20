@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup-DeepSearch.ps1"
set "DEEPSEARCH_EXIT=%ERRORLEVEL%"
pause
exit /b %DEEPSEARCH_EXIT%
