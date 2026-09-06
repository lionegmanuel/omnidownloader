@echo off
title OmniDownloader Motor Local Daemon (localhost:18989)
color 0B
echo =======================================================
echo         OMNIDOWNLOADER PRO - MOTOR LOCAL DAEMON
echo =======================================================
echo.

cd /d "%~dp0"

if not exist "server\venv\Scripts\activate.bat" (
    color 0E
    echo [AVISO] El entorno virtual no existe. Ejecutando instalacion primero...
    call install.bat
)

call server\venv\Scripts\activate.bat

echo Iniciando servidor en http://127.0.0.1:18989...
echo (Manten esta ventana abierta mientras uses la extension en Chrome)
echo.

server\venv\Scripts\python.exe server\run.py

pause

