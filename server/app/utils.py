import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional
from .config import settings

def sanitize_filename(filename: str, max_length: int = 120) -> str:
    """
    Limpia caracteres no permitidos en nombres de archivo de Windows y limita longitud.
    """
    if not filename:
        return "video"
    # Reemplazar caracteres prohibidos en Windows por guiones bajos
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', '_', filename)
    # Limpiar espacios consecutivos y recortar bordes
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ._')
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip(' ._')
    return cleaned or "video"

def open_in_file_manager(target_path: Optional[str] = None) -> bool:
    """
    Abre el explorador de Windows seleccionando el archivo o abriendo la carpeta de descargas.
    Garantiza que en Windows nunca se abra 'Documentos' por argumentos mal parseados de explorer.exe.
    """
    try:
        # Si target_path es relativo, intentar resolverlo respecto a DOWNLOAD_DIR
        if target_path and not os.path.isabs(target_path):
            candidate = settings.DOWNLOAD_DIR / target_path
            if candidate.exists():
                target_path = str(candidate)

        if target_path and os.path.exists(target_path):
            abs_path = os.path.normpath(os.path.abspath(target_path))
            if sys.platform == "win32":
                if os.path.isfile(abs_path):
                    # IMPORTANTE: En Windows, explorer.exe requiere que la opción /select quede
                    # fuera de las comillas: explorer /select,"D:\ruta con espacios\archivo.ext"
                    # Si se pasa como lista a subprocess.Popen, Python entrecomilla todo el argumento
                    # ("/..."), lo que causa que explorer.exe falle y abra 'Documentos'.
                    subprocess.Popen(f'explorer /select,"{abs_path}"')
                else:
                    os.startfile(abs_path)
                return True
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", abs_path])
                return True
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(abs_path) if os.path.isfile(abs_path) else abs_path])
                return True
        else:
            # Si no hay archivo o no existe, abrir la carpeta de descargas configurada (D:\Documents\MANUEL\OmniDownloader)
            folder = os.path.normpath(str(settings.DOWNLOAD_DIR))
            os.makedirs(folder, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(folder)
                return True
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
                return True
            else:
                subprocess.Popen(["xdg-open", folder])
                return True
    except Exception as e:
        print(f"[ERROR] Error al abrir explorador de archivos: {e}")
        return False

def format_bytes(bytes_num: Optional[int] = None) -> str:
    if not bytes_num:
        return "0 B"
    num = float(bytes_num)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"

def format_seconds(seconds: Optional[int] = None) -> str:
    if not seconds:
        return "00:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


