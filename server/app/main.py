import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import yt_dlp

from .config import settings
from .models import (
    HealthResponse,
    InfoRequest,
    InfoResponse,
    DownloadRequest,
    DownloadResponse,
    ProgressResponse,
    OpenFolderRequest,
    StatusResponse
)
from .downloader import MediaDownloader
from .progress import task_manager
from .utils import open_in_file_manager

app = FastAPI(
    title="OmniDownloader Engine",
    description="Motor local privado para descarga y procesamiento de medios en alta calidad",
    version="1.0.0"
)

# Permitir todas las peticiones (extensiones de Chrome chrome-extension:// y localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        ffmpeg_available=bool(settings.FFMPEG_PATH),
        ffmpeg_path=settings.FFMPEG_PATH or "No detectado en PATH ni bin/",
        yt_dlp_version=yt_dlp.version.__version__,
        download_dir=str(settings.DOWNLOAD_DIR)
    )

@app.post("/api/info", response_model=InfoResponse)
def extract_media_info(req: InfoRequest):
    try:
        data = MediaDownloader.extract_info(
            url=req.url,
            headers=req.headers,
            cookies=req.cookies
        )
        return InfoResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo extraer información: {str(e)}")

@app.post("/api/download", response_model=DownloadResponse)
def start_download(req: DownloadRequest):
    task_id = str(uuid.uuid4())
    title = req.title or "Descarga Multimedia"

    # Registrar tarea inicial
    task_manager.create_task(task_id=task_id, title=title)

    # Disparar descarga en pool asíncrono
    MediaDownloader.start_download_async(
        task_id=task_id,
        url=req.url,
        quality_profile=req.quality_profile,
        format_id=req.format_id or "best",
        headers=req.headers,
        title=title,
        cookies=req.cookies
    )

    return DownloadResponse(
        task_id=task_id,
        status="queued",
        title=title,
        message="Descarga iniciada exitosamente"
    )

@app.get("/api/progress/{task_id}", response_model=ProgressResponse)
def get_progress(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.get("/api/tasks", response_model=List[ProgressResponse])
def get_all_tasks():
    return task_manager.list_tasks()

@app.post("/api/open-folder", response_model=StatusResponse)
def open_folder(req: OpenFolderRequest):
    success = open_in_file_manager(req.file_path)
    if success:
        return StatusResponse(success=True, message="Explorador de archivos abierto")
    return StatusResponse(success=False, message="No se pudo abrir el explorador")

