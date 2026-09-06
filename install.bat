@echo off
title Instalador OmniDownloader Pro
color 0A
echo =======================================================
echo          INSTALADOR OMNIDOWNLOADER PRO
echo =======================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org/
    echo Asegurate de marcar la opcion "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [2/3] Creando entorno virtual de Python en server\venv...
if not exist "server\venv" (
    python -m venv server\venv
)

echo [3/3] Instalando dependencias de server\requirements.txt...
call server\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r server\requirements.txt

echo.
echo =======================================================
echo     INSTALACION COMPLETADA CON EXITO!
echo =======================================================
echo Ya puedes iniciar el motor ejecutando start_server.bat
echo.
pause

