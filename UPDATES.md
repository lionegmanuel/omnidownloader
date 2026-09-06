# UPDATES — Registro de sesiones de trabajo (OmniDownloader Pro)

Este archivo es el changelog contextual de este repo: cada sesión trabajada se resume acá (qué se hizo, qué se verificó, decisiones relevantes y qué quedó pendiente). Entradas más recientes arriba. Sirve para retomar contexto rápido sin releer el historial completo de conversaciones. **Retención: solo persisten los últimos 3 días de fecha (hoy + 2 días atrás) — al agregar la entrada de una nueva sesión, se elimina toda entrada con más de 2 días de antigüedad respecto a esa fecha** (regla de `CLAUDE.md` sección 5).

---

## 2026-09-06 — Configuración de ruta definitiva (`D:\Documents\MANUEL\OmniDownloader`) y corrección de apertura de Windows Explorer

**Pedido de Manuel:**

1. Solucionar el fallo en el botón "Abrir" donde Windows abría la carpeta "Documentos" por defecto en lugar de resaltar el video descargado.
2. Fijar la ruta de descarga permanente de cada archivo a `D:\Documents\MANUEL\OmniDownloader`.

**Implementado:**

- `server/app/utils.py`: Corrección en `open_in_file_manager`. Se eliminó la invocación como lista `['explorer', f'/select,{abs_path}']` (la cual generaba `explorer "/select,..."` al haber espacios en la ruta, rompiendo el switch `/select` de Windows Explorer y provocando el fallback indeseado a la carpeta "Documentos"). Se sustituyó por `subprocess.Popen(f'explorer /select,"{abs_path}"')` con comillas estrictamente alrededor de la ruta normalizada. Se agregó además resolución para rutas relativas y fallback a la carpeta configurada.
- `server/app/config.py`: Definición de `DEFAULT_DOWNLOAD_DIR = Path("D:/Documents/MANUEL/OmniDownloader")`, forzando siempre esta ruta tanto si no se define `.env` como si se intenta apuntar al disco C:.
- `.env` y `.env.example`: Actualizada la clave `DOWNLOAD_DIR=D:/Documents/MANUEL/OmniDownloader`.
- `CLAUDE.md` y `README.md`: Documentación técnica y manual de usuario actualizados con la ruta exacta `D:\Documents\MANUEL\OmniDownloader\`.

- `extension/popup/popup.js`: Implementada selección inteligente de URL en el botón principal de descarga (`handleCurrentDownload`). En sitios de noticias o portales genéricos protegidos por CDNs (como TN, Clarín o Infobae) donde el scraping directo de la página arroja `HTTP 400 Bad Request`, la extensión ahora prioriza automáticamente el stream directo interceptado (`.m3u8` o `.mp4`) capturado por el sniffer de red, haciendo que el botón principal descargue de inmediato sin requerir intervención manual del usuario.

**Verificado:**

- Confirmada la descarga y ensamblado de video HLS (`.m3u8`) a través del sniffer y apertura exitosa en Windows Explorer (`POST /api/open-folder HTTP 200 OK`).
- Tests automatizados en `server/tests/test_api.py` corriendo 8/8 aprobados con `pytest`.
- Verificada la sintaxis de invocación de `explorer.exe` y la resolución de directorios en disco D:.

---

## 2026-09-06 — Reubicación estricta de descargas al disco D: (`D:\Downloads\OmniDownloader`)

**Pedido de Manuel:** Garantizar que absolutamente nada se almacene en el disco C:, forzando que todas las descargas se guarden exclusivamente en el disco D:.

**Implementado:**

- `server/app/config.py`: Regla innegociable de resolución de `DOWNLOAD_DIR`. Si existe la unidad `D:`, fuerza la ruta `D:\Downloads\OmniDownloader` por defecto y redirige cualquier configuración que intente apuntar a `C:`.
- `.env` y `.env.example`: Actualizada la variable `DOWNLOAD_DIR=D:/Downloads/OmniDownloader`.
- `README.md`: Manual y referencias actualizadas para documentar el destino en `D:\Downloads\OmniDownloader\`.
- Limpieza: Eliminado directorio temporal vacío residual en el disco C:.
- `server/tests/test_api.py`: Incorporada aserción explícita en `test_health_endpoint` validando que `download_dir` inicie estrictamente con la unidad `D:`.

**Verificado:**

- Pytest: 8/8 pruebas pasando al 100% en `server/venv`.
- Python REPL confirma resolución exacta: `D:\Downloads\OmniDownloader`.

**Pendiente real para la próxima sesión:**

- Manuel revisará la app visualmente en Google Chrome y creará el repositorio remoto en GitHub para subir el código.

---

## 2026-09-05 — Construcción, integración y validación end-to-end de OmniDownloader Pro

**Pedido de Manuel:** Estar a cargo del desarrollo integral de punta a punta (0 a 100) de OmniDownloader Pro en `D:\Documents\MANUEL\DEV\video-downloader` bajo la regla de ejecución continua sin interrupciones, construyendo y validando tanto el backend (Python FastAPI + yt-dlp + FFmpeg) como la extensión Chrome MV3 y scripts Windows.

**Implementado:**

- **Backend Local (`server/`):**
  - Creación del entorno virtual `server\venv` con dependencias instaladas y fijadas en `requirements.txt` (`fastapi`, `uvicorn[standard]`, `yt-dlp`, `pydantic`, `python-dotenv`, `requests`, `httpx`, `pytest`).
  - `server/app/config.py`: Detección automática del binario FFmpeg en el sistema (detectado en WinGet Packages) y directorio de descargas resuelto en `C:\Users\MANUEL\Downloads\OmniDownloader`.
  - `server/app/models.py`: Modelos Pydantic tipados para `/health`, `/api/info`, `/api/download`, `/api/progress/{task_id}`, `/api/tasks` y `/api/open-folder`.
  - `server/app/downloader.py`: Integración concurrente con `yt_dlp.YoutubeDL` en `ThreadPoolExecutor`. Inyección de cabeceras HTTP (`Referer`, `User-Agent`) y `Cookie` para el bypass de errores 403. Limpieza de secuencias ANSI en reportes de velocidad (`MB/s`), `postprocessor_hooks` para reportar estado `"merging"` con FFmpeg, unión limpia de video/audio y extracción a MP3 a 320 kbps. Resolución precisa del archivo final en disco.
  - `server/app/progress.py`: Almacén concurrente thread-safe para seguimiento de tareas activas y terminadas.
  - `server/app/utils.py`: Sanitización de nombres de archivo para Windows NTFS (`sanitize_filename`), formateo de bytes y tiempo, y apertura de Windows Explorer con selección de archivo (`explorer.exe /select`).
  - `server/app/main.py`: Configuración de FastAPI con CORS permisivo (`*`) y todos los endpoints REST.
  - `server/run.py`: Script de arranque en puerto `18989` con `app_dir` especificado para compatibilidad en Windows.
- **Frontend / Extensión Chrome Manifest V3 (`extension/`):**
  - `extension/manifest.json`: Manifest V3 con permisos `activeTab`, `tabs`, `storage`, `webRequest`, `contextMenus`, host permissions `<all_urls>` y `http://127.0.0.1:18989/*`, con iconos top-level y action icons en 16, 48 y 128 px.
  - `extension/background/service_worker.js`: Sniffer pasivo de tráfico multimedia (`.m3u8`, `.mpd`, `.mp4`, `.webm`, `video/*`, `audio/*`), persistencia resiliente en `chrome.storage.session` (inmune a la suspensión del service worker), badge numérico esmeralda y menú contextual nativo _"Descargar con OmniDownloader"_.
  - `extension/content/content_script.js`: Inyector para capturar videos del DOM (`<video>`, `<source>`, `<audio>`), thumbnails (`og:image`, `poster`) y `document.cookie` para emulación de sesión.
  - `extension/popup/popup.html` & `popup.css`: Interfaz Dark Glassmorphism, selector de 4 calidades (Mejor calidad 4K/1080p, 1080p, 720p, Solo Audio MP3), acordeón de streams directos detectados, barras de progreso animadas y botón directo _"📂 Abrir"_.
  - `extension/popup/popup.js`: Lógica en Vanilla JS con verificación de salud del backend, polling en tiempo real y disparador de descargas.
- **Automatización y Configuración:**
  - `install.bat`: Script 1-click para crear el entorno virtual e instalar requerimientos.
  - `start_server.bat`: Script de inicio que invoca directamente el ejecutable `server\venv\Scripts\python.exe`.
  - `.env`: Archivo de entorno local activo basado en `.env.example`.
  - `.gitignore`: Configuración completa para Python, venv, secretos, binarios, temporales y SO.
  - `CLAUDE.md`: Incorporadas las directivas de registro de sesiones en `UPDATES.md` y regla de retención de 3 días.

**Verificado:**

- Suite de 8 tests automatizados en `server/tests/test_api.py` corriendo con `pytest` en `server\venv` (`8 passed in 0.99s`).
- Verificación de API en vivo (`127.0.0.1:18989`):
  - `GET /health` responde 200 OK con detección de FFmpeg y versión de yt-dlp.
  - `POST /api/info` extrajo metadatos y formatos de un stream HLS (`.m3u8`) en milisegundos.
  - `POST /api/download` ejecutó exitosamente la descarga de video (`.mp4`) y la extracción/conversión de audio (`.mp3` 320k) en `C:\Users\MANUEL\Downloads\OmniDownloader`.
  - `POST /api/open-folder` verificado en Windows Explorer.

**Pendiente real para la próxima sesión:**

- Manuel revisará la app visualmente en Google Chrome y creará el repositorio remoto en GitHub para subir el código.
