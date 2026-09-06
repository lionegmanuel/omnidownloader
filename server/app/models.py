from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    ffmpeg_available: bool
    ffmpeg_path: str
    yt_dlp_version: str
    download_dir: str

class InfoRequest(BaseModel):
    url: str
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[str] = None

class FormatInfo(BaseModel):
    format_id: str
    label: str
    resolution: str
    ext: str
    filesize_approx: Optional[str] = None

class InfoResponse(BaseModel):
    id: str
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    duration_string: Optional[str] = None
    extractor: str
    is_stream: bool = False
    formats: List[FormatInfo] = []

class DownloadRequest(BaseModel):
    url: str
    title: Optional[str] = None
    format_id: Optional[str] = "best"
    quality_profile: str = Field(default="best", description="best | 1080p | 720p | audio_only")
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[str] = None

class DownloadResponse(BaseModel):
    task_id: str
    status: str
    title: str
    message: str

class ProgressResponse(BaseModel):
    task_id: str
    status: str  # queued, downloading, merging, finished, error
    progress_percent: float = 0.0
    speed: Optional[str] = None
    eta_seconds: Optional[int] = None
    downloaded_bytes: Optional[int] = None
    total_bytes: Optional[int] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None

class OpenFolderRequest(BaseModel):
    file_path: Optional[str] = None

class StatusResponse(BaseModel):
    success: bool
    message: str

