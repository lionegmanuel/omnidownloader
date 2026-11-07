#!/usr/bin/env bash
# Motor local de OmniDownloader en Linux (equivale a install.bat + start_server.bat)
set -e
cd "$(dirname "$0")"
if [ ! -x server/venv/bin/python ]; then
  echo "[AVISO] Creando el entorno virtual en server/venv..."
  python3 -m venv server/venv
  server/venv/bin/python -m pip install --upgrade pip
  server/venv/bin/pip install -r server/requirements.txt
fi
echo "Iniciando servidor en http://127.0.0.1:18989 (dejá esta terminal abierta mientras uses la extensión)"
exec server/venv/bin/python server/run.py
