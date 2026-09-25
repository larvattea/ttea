@echo off
rem Cria o ambiente virtual .venv e instala as dependencias do T-TEA.
rem Para usar um Python especifico: set PYTHON=C:\caminho\python.exe
setlocal
cd /d "%~dp0"

if not defined PYTHON (
    py -3 --version >nul 2>&1 && set "PYTHON=py -3"
)
if not defined PYTHON (
    python --version >nul 2>&1 && set "PYTHON=python"
)
if not defined PYTHON (
    for /d %%D in ("%ProgramFiles%\Python3*" "%LocalAppData%\Programs\Python\Python3*") do (
        if exist "%%~D\python.exe" set PYTHON="%%~D\python.exe"
    )
)
if not defined PYTHON (
    echo Python nao encontrado. Instale o Python 3.8-3.11 ou defina a variavel PYTHON.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual com %PYTHON%...
    %PYTHON% -m venv .venv || goto erro
)
".venv\Scripts\python.exe" -m pip install --upgrade pip || goto erro
".venv\Scripts\python.exe" -m pip install -r requisitos.txt || goto erro
echo.
echo Pronto. Execute T-TEA.bat para iniciar.
pause
exit /b 0

:erro
echo Falha na instalacao.
pause
exit /b 1
