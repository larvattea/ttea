@echo off
setlocal
cd /d "%~dp0Source"

if not exist "..\.venv\Scripts\python.exe" (
    echo Ambiente nao configurado. Execute "Preparando o python.bat" primeiro.
    pause
    exit /b 1
)
"..\.venv\Scripts\python.exe" TTEA_menu.py
