import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Asegurar importación de la app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.config import settings
from app.utils import sanitize_filename, format_bytes, format_seconds
from app.downloader import MediaDownloader
from app.progress import task_manager

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ffmpeg_available" in data
    assert "yt_dlp_version" in data
    assert "download_dir" in data
    assert data["download_dir"].lower().startswith("d:")

def test_sanitize_filename():
    assert sanitize_filename("video:title/test*name?|<>") == "video_title_test_name"
    assert sanitize_filename("   hello   world   ") == "hello world"
    assert sanitize_filename("") == "video"
    long_name = "a" * 200
    assert len(sanitize_filename(long_name)) <= 120

def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(500) == "500.0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024 * 5) == "5.0 MB"

def test_format_seconds():
    assert format_seconds(0) == "00:00"
    assert format_seconds(45) == "00:45"
    assert format_seconds(125) == "02:05"
    assert format_seconds(3665) == "01:01:05"

def test_ydl_base_opts_with_headers_and_cookies():
    headers = {
        "User-Agent": "TestUA/1.0",
        "Referer": "https://example.com/page",
        "X-Custom-Ignore": "ignored"
    }
    cookies = "sessionid=xyz123; user=manuel"
    opts = MediaDownloader._build_ydl_base_opts(headers=headers, cookies=cookies)

    assert opts["quiet"] is True
    assert opts["no_color"] is True
    assert "http_headers" in opts
    assert opts["http_headers"]["User-Agent"] == "TestUA/1.0"
    assert opts["http_headers"]["Referer"] == "https://example.com/page"
    assert opts["http_headers"]["Cookie"] == cookies
    assert "X-Custom-Ignore" not in opts["http_headers"]

def test_tasks_lifecycle():
    # 1. Crear tarea de descarga
    res = client.post("/api/download", json={
        "url": "https://example.com/fake_stream.m3u8",
        "title": "Prueba Streaming",
        "quality_profile": "best"
    })
    assert res.status_code == 200
    data = res.json()
    task_id = data["task_id"]
    assert data["status"] == "queued"

    # 2. Consultar progreso de la tarea
    res_progress = client.get(f"/api/progress/{task_id}")
    assert res_progress.status_code == 200
    p_data = res_progress.json()
    assert p_data["task_id"] == task_id
    assert p_data["status"] in ("queued", "downloading", "error", "finished")

    # 3. Listar tareas
    res_tasks = client.get("/api/tasks")
    assert res_tasks.status_code == 200
    tasks = res_tasks.json()
    assert any(t["task_id"] == task_id for t in tasks)

def test_progress_not_found():
    response = client.get("/api/progress/non-existent-task-id")
    assert response.status_code == 404

def test_open_folder_endpoint():
    response = client.post("/api/open-folder", json={})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data

