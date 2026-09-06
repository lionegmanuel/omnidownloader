import os
import sys
import uvicorn

# Asegurar que el directorio raíz de server esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

if __name__ == "__main__":
    print(f"[*] Iniciando OmniDownloader Server en {settings.HOST}:{settings.PORT}")
    print(f"[*] Carpeta de descargas: {settings.DOWNLOAD_DIR}")
    server_dir = os.path.dirname(os.path.abspath(__file__))
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        app_dir=server_dir,
        log_level="info"
    )

