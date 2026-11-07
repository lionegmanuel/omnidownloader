import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe (override=True para que siempre mande .env)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "18989"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Directorio de Descargas (Estrictamente en disco D: - D:\Documents\MANUEL\OmniDownloader)
    # En Linux (Fedora) el D: de Windows es /mnt/d (se cambia con VX_RAIZ_D)
    RAIZ_D = "D:/" if os.name == "nt" else os.getenv("VX_RAIZ_D", "/mnt/d").rstrip("/") + "/"
    DEFAULT_DOWNLOAD_DIR = Path(RAIZ_D + "Documents/MANUEL/OmniDownloader")
    custom_download_dir = os.getenv("DOWNLOAD_DIR", "").strip()
    if os.name != "nt" and custom_download_dir[:2].lower() == "d:":
        custom_download_dir = RAIZ_D + custom_download_dir[2:].replace("\\", "/").lstrip("/")
    if custom_download_dir:
        candidate = Path(os.path.expanduser(custom_download_dir))
    else:
        candidate = DEFAULT_DOWNLOAD_DIR

    # Regla innegociable: no guardar nada en C:, forzar disco D: siempre
    if str(candidate).lower().startswith("c:"):
        candidate = DEFAULT_DOWNLOAD_DIR

    DOWNLOAD_DIR: Path = candidate
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Detección de FFmpeg
    custom_ffmpeg = os.getenv("FFMPEG_PATH", "").strip()
    bin_ffmpeg = Path(__file__).resolve().parent.parent / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")

    if custom_ffmpeg and os.path.exists(custom_ffmpeg):
        FFMPEG_PATH: str = custom_ffmpeg
    elif bin_ffmpeg.exists():
        FFMPEG_PATH: str = str(bin_ffmpeg)
    elif shutil.which("ffmpeg"):
        FFMPEG_PATH: str = shutil.which("ffmpeg") or "ffmpeg"
    else:
        FFMPEG_PATH: str = ""

    MAX_PARALLEL_DOWNLOADS: int = int(os.getenv("MAX_PARALLEL_DOWNLOADS", "3"))

settings = Settings()

