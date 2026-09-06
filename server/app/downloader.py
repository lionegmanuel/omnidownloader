import os
import re
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import yt_dlp

from .config import settings
from .models import InfoResponse, FormatInfo
from .progress import task_manager
from .utils import sanitize_filename, format_bytes

executor = ThreadPoolExecutor(max_workers=settings.MAX_PARALLEL_DOWNLOADS)

class MediaDownloader:
    @staticmethod
    def _build_ydl_base_opts(headers: Optional[Dict[str, str]] = None, cookies: Optional[str] = None) -> Dict[str, Any]:
        opts: Dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'noplaylist': True,
            'no_color': True,
        }

        # Configurar ubicación de FFmpeg si existe
        if settings.FFMPEG_PATH:
            opts['ffmpeg_location'] = settings.FFMPEG_PATH

        # Cabeceras personalizadas (Referer, User-Agent, Cookies, etc.)
        http_headers: Dict[str, str] = {}
        if headers:
            for k, v in headers.items():
                if k.lower() in ('user-agent', 'referer', 'origin', 'authorization', 'cookie'):
                    http_headers[k] = v

        if cookies and 'Cookie' not in http_headers and 'cookie' not in http_headers:
            http_headers['Cookie'] = cookies

        if http_headers:
            opts['http_headers'] = http_headers

        return opts

    @classmethod
    def extract_info(cls, url: str, headers: Optional[Dict[str, str]] = None, cookies: Optional[str] = None) -> Dict[str, Any]:
        opts = cls._build_ydl_base_opts(headers, cookies)
        opts['extract_flat'] = False

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                # Si falla, intentar modo genérico para m3u8 o mpd
                opts['force_generic_extractor'] = True
                with yt_dlp.YoutubeDL(opts) as ydl_gen:
                    info = ydl_gen.extract_info(url, download=False)

        if not info:
            raise ValueError("No se pudo extraer información del recurso multimedia.")

        title = info.get('title') or "Video Sin Título"
        video_id = info.get('id') or str(uuid.uuid4())[:8]
        thumbnail = info.get('thumbnail')
        duration = info.get('duration')
        extractor = info.get('extractor') or "generic"

        # Identificar si es un stream directo .m3u8 o .mpd
        is_stream = bool(re.search(r'\.(m3u8|mpd)', url, re.IGNORECASE))

        formats_list = [
            FormatInfo(
                format_id="best",
                label="💎 Mejor calidad disponible (Automático 4K/1080p)",
                resolution="Máxima",
                ext="mp4"
            ),
            FormatInfo(
                format_id="1080p",
                label="🎬 1080p Full HD",
                resolution="1920x1080",
                ext="mp4"
            ),
            FormatInfo(
                format_id="720p",
                label="📱 720p HD",
                resolution="1280x720",
                ext="mp4"
            ),
            FormatInfo(
                format_id="audio_only",
                label="🎵 Solo Audio (MP3 alta calidad)",
                resolution="Audio",
                ext="mp3"
            ),
        ]

        return {
            "id": str(video_id),
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "duration_string": f"{duration//60}:{duration%60:02d}" if duration else None,
            "extractor": extractor,
            "is_stream": is_stream,
            "formats": [f.model_dump() for f in formats_list]
        }

    @classmethod
    def _execute_download_sync(
        cls,
        task_id: str,
        url: str,
        quality_profile: str,
        format_id: str,
        headers: Optional[Dict[str, str]],
        title: Optional[str],
        cookies: Optional[str] = None
    ):
        opts = cls._build_ydl_base_opts(headers, cookies)

        # Plantilla de salida limpia en la carpeta de descargas
        if title and title.strip() and title not in ("Video", "Descarga Multimedia", "Video Web"):
            safe_title = sanitize_filename(title)
            outtmpl = os.path.join(str(settings.DOWNLOAD_DIR), f"{safe_title} [%(id)s].%(ext)s")
        else:
            outtmpl = os.path.join(str(settings.DOWNLOAD_DIR), "%(title).100B [%(id)s].%(ext)s")

        opts['outtmpl'] = outtmpl
        opts['updatetime'] = False

        # Configurar calidad y post-procesadores
        if quality_profile == "audio_only":
            opts['format'] = 'bestaudio/best'
            if settings.FFMPEG_PATH:
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }]
        elif quality_profile == "1080p":
            opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            opts['merge_output_format'] = 'mp4'
        elif quality_profile == "720p":
            opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            opts['merge_output_format'] = 'mp4'
        elif format_id and format_id not in ("best", "1080p", "720p", "audio_only"):
            opts['format'] = f"{format_id}+bestaudio/best"
            opts['merge_output_format'] = 'mp4'
        else:  # "best"
            opts['format'] = 'bestvideo+bestaudio/best'
            opts['merge_output_format'] = 'mp4'

        def progress_hook(d):
            status = d.get('status')
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes') or 0
                percent = 0.0
                if total > 0:
                    percent = round((downloaded / total) * 100, 1)
                elif '_percent_str' in d:
                    try:
                        clean_pct = re.sub(r'[^\d.]', '', d['_percent_str'])
                        percent = float(clean_pct) if clean_pct else 0.0
                    except Exception:
                        pass

                raw_speed = d.get('_speed_str', '')
                clean_speed = re.sub(r'\x1b\[[0-9;]*m', '', raw_speed).strip() if raw_speed else None
                if not clean_speed and d.get('speed'):
                    clean_speed = f"{format_bytes(d['speed'])}/s"

                eta_s = d.get('eta')

                task_manager.update_task(
                    task_id,
                    status="downloading",
                    progress_percent=percent,
                    speed=clean_speed,
                    eta_seconds=eta_s,
                    downloaded_bytes=downloaded,
                    total_bytes=total
                )
            elif status == 'finished':
                task_manager.update_task(
                    task_id,
                    status="merging",
                    progress_percent=99.0,
                    speed="Uniendo audio y video..."
                )

        def postprocessor_hook(d):
            if d.get('status') == 'started':
                task_manager.update_task(
                    task_id,
                    status="merging",
                    progress_percent=99.0,
                    speed="Procesando / Uniendo con FFmpeg..."
                )

        opts['progress_hooks'] = [progress_hook]
        opts['postprocessor_hooks'] = [postprocessor_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Resolver archivo final exacto
                final_path = None
                if info and 'requested_downloads' in info and info['requested_downloads']:
                    req_dl = info['requested_downloads'][0]
                    final_path = req_dl.get('filepath') or req_dl.get('_filename')

                if not final_path or not os.path.exists(final_path):
                    prep = ydl.prepare_filename(info) if info else ""
                    if prep:
                        base = os.path.splitext(prep)[0]
                        if quality_profile == "audio_only":
                            for ext in ('.mp3', '.m4a', '.opus', '.aac', '.wav'):
                                if os.path.exists(base + ext):
                                    final_path = base + ext
                                    break
                            if not final_path:
                                final_path = base + ".mp3"
                        elif opts.get('merge_output_format') == 'mp4':
                            if os.path.exists(base + ".mp4"):
                                final_path = base + ".mp4"
                            elif os.path.exists(prep):
                                final_path = prep
                            else:
                                final_path = base + ".mp4"
                        else:
                            final_path = prep

                clean_name = os.path.basename(final_path) if final_path else "video.mp4"
                abs_final_path = os.path.abspath(final_path) if final_path else ""

                task_manager.update_task(
                    task_id,
                    status="finished",
                    progress_percent=100.0,
                    filename=clean_name,
                    file_path=abs_final_path,
                    speed=None,
                    eta_seconds=0
                )
        except Exception as e:
            err_msg = str(e)
            try:
                print(f"[ERROR Download Task {task_id}] {err_msg}")
            except Exception:
                pass
            task_manager.update_task(
                task_id,
                status="error",
                error=err_msg
            )

    @classmethod
    def start_download_async(
        cls,
        task_id: str,
        url: str,
        quality_profile: str,
        format_id: str,
        headers: Optional[Dict[str, str]],
        title: Optional[str],
        cookies: Optional[str] = None
    ):
        executor.submit(
            cls._execute_download_sync,
            task_id,
            url,
            quality_profile,
            format_id,
            headers,
            title,
            cookies
        )

