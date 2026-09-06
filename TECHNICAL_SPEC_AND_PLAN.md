# OmniDownloader — Plan Técnico y Especificación de Arquitectura End-to-End (0 a 100)

> **Destinatario:** Ingeniero / Desarrollador Full-Stack a cargo del desarrollo completo.
> **Alcance:** Creación integral de una solución privada de descarga de video sin límites (Extensión Chrome MV3 + Motor Local en Python con yt-dlp & FFmpeg).
> **Mandato:** Desarrollo y ejecución de punta a punta (End-to-End) sin interrupciones. Si surgen advertencias o ajustes menores, se resuelven de forma autónoma y se documentan al final.

---

## 1. VISIÓN GENERAL Y OBJETIVO DEL PRODUCTO

### 1.1 El Problema con las Extensiones Comerciales (Ej. Video DownloadHelper)

Las extensiones de la Chrome Web Store sufren de tres graves problemas:

1. **Restricción comercial / Paywalls:** Limitan la velocidad, imponen colas de espera (1 video cada 2 horas) o incrustan marcas de agua (QR) a menos que se pague una licencia premium (~$28 USD).
2. **Censura de YouTube en Chrome:** Por normativas de Google Web Store, las extensiones comerciales tienen prohibido por contrato descargar de YouTube en Chrome.
3. **Limitación de Sandbox del Navegador:** Los navegadores no pueden transcodificar formatos pesados o unir streams separados (audio + video HLS/DASH en 1080p, 4K, 8K) de forma eficiente sin un software complementario nativo.

### 1.2 La Solución: OmniDownloader

Una herramienta privada, moderna, potente y **100% ilimitada** dividida en dos capas:

1. **Extensión de Navegador (Chrome MV3):** Funciona como sniffer de tráfico de red, interceptor de peticiones multimedia (`.mp4`, `.m3u8`, `.mpd`), detector de contexto de página (YouTube, Vimeo, Twitter/X, Instagram, TikTok, Facebook, webs de cursos, etc.) y panel de control visual para el usuario.
2. **Motor Local (FastAPI + yt-dlp + FFmpeg):** Un daemon local corriendo en `http://127.0.0.1:18989`. Recibe la URL o stream junto con las cabeceras de autenticación (cookies/referer) y utiliza las mejores herramientas open-source para descargar a máxima velocidad de hardware, realizar muxing de audio/video en 4K/60fps y guardar el archivo directamente en la carpeta de Descargas del usuario.

---

## 2. ARQUITECTURA DEL SISTEMA

```
+---------------------------------------------------------------------------------------+
| NAVEGADOR WEB (Google Chrome / Brave / Edge)                                         |
|                                                                                       |
|  [ Pestaña Web: YouTube, Twitter, Stream Embed, Web de Cursos, etc. ]                 |
|       |                                                                               |
|       v                                                                               |
|  [ Content Script & Media Sniffer ]                                                   |
|       * Intercepta peticiones fetch/xhr y tags <video> / <source>                     |
|       * Captura URL del stream (.m3u8, .mpd, .mp4)                                    |
|       * Extrae Cookies de sesión, User-Agent, Referer                                 |
|       |                                                                               |
|       v                                                                               |
|  [ Background Service Worker (MV3) ]                                                  |
|       * Mantiene diccionario de streams detectados por Tab ID                         |
|       * Actualiza Badge del ícono (1, 2, 3...)                                        |
|       * Menú contextual: "Descargar video con OmniDownloader"                         |
|       |                                                                               |
|       v                                                                               |
|  [ Popup UI (Extensión) ]                                                             |
|       * Muestra info del video actual (Título, Thumbnail, Duración)                   |
|       * Selector de calidad: Best (4K/1080p), 1080p, 720p, Solo Audio (MP3)           |
|       * Lista de streams directos (.m3u8 / .mp4) si es un reproductor genérico         |
|       * Barra de progreso en tiempo real (Polling / SSE)                              |
+---------------------------------------------------------------------------------------+
                                        |
                 HTTP REST / SSE Calls  | (http://127.0.0.1:18989)
                                        v
+---------------------------------------------------------------------------------------+
| SERVIDOR LOCAL / MOTOR DAEMON (Python FastAPI + yt-dlp + FFmpeg)                      |
|                                                                                       |
|  [ FastAPI Server (localhost:18989) ]                                                 |
|       * GET  /health          -> Chequeo de conexión y estado de ffmpeg/yt-dlp        |
|       * POST /api/info        -> Extrae metadatos y formatos disponibles              |
|       * POST /api/download    -> Dispara tarea de descarga asíncrona                  |
|       * GET  /api/progress    -> Progreso en tiempo real (% completado, velocidad, ETA|
|       * POST /api/open-folder -> Abre explorador de archivos en carpeta destino       |
|                                                                                       |
|  [ Motor yt-dlp Core ]                                                                |
|       * Maneja 1.800+ extractores nativos                                             |
|       * Soporte de manifests HLS (.m3u8) y DASH (.mpd)                                |
|       * Inyección de cookies de navegador para saltar protecciones 403 Forbidden      |
|                                                                                       |
|  [ FFmpeg Binario ]                                                                   |
|       * Ensamblado sin pérdida (Muxing) de pista de video 4K/1080p con pista de audio |
|       * Conversión a MP3/M4A cuando se solicita solo audio                            |
|                                                                                       |
|  [ Almacenamiento Local ]                                                             |
|       * Directorio de Descargas: C:\Users\<USER>\Downloads\OmniDownloader             |
+---------------------------------------------------------------------------------------+
```

---

## 3. ESPECIFICACIÓN TÉCNICA DEL MOTOR LOCAL (BACKEND)

### 3.1 Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Framework Web:** FastAPI + Uvicorn
- **Motor de Descarga:** `yt-dlp` (última versión vía pip)
- **Procesador Multimedia:** `ffmpeg` (en el PATH del sistema o binario en `server/bin/`)
- **Validación y Configuración:** `pydantic`, `pydantic-settings`, `python-dotenv`
- **Concurrencia:** `asyncio` y `ThreadPoolExecutor` para descargas paralelas sin bloquear el loop de eventos.

### 3.2 Estructura de Directorios del Proyecto

```
video-downloader/
├── CLAUDE.md                    # Contexto operativo para agentes y Claude Code
├── TECHNICAL_SPEC_AND_PLAN.md   # Esta especificación técnica completa
├── START_DEV_PROMPT.md          # Prompt de inicio para el dev
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Exclusiones de Git
├── README.md                    # Manual de usuario y troubleshooting
├── install.bat                  # Script de instalación Windows 1-click
├── start_server.bat             # Script de inicio del servidor en Windows
│
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Entrypoint de FastAPI y configuración de CORS
│   │   ├── config.py            # Carga de variables de entorno y paths
│   │   ├── models.py            # Modelos Pydantic para requests y responses
│   │   ├── downloader.py        # Wrapper sobre yt-dlp y hooks de progreso
│   │   ├── progress.py          # Gestor en memoria de tareas y estados
│   │   └── utils.py             # Utilidades de sistema (abrir carpeta, detectar ffmpeg)
│   ├── bin/                     # Directorio opcional para ffmpeg.exe
│   ├── requirements.txt         # Dependencias pip
│   └── run.py                   # Script de inicio directo python run.py
│
└── extension/
    ├── manifest.json            # Manifest V3 de Chrome
    ├── background/
    │   └── service_worker.js    # Sniffer de peticiones de red y badges
    ├── content/
    │   └── content_script.js    # Extractor de metadatos del DOM
    ├── popup/
    │   ├── popup.html           # Interfaz de usuario (Glassmorphism dark mode)
    │   ├── popup.css            # Estilos modernos, responsive, badges
    │   └── popup.js             # Lógica cliente, conexión a API local y estados
    └── icons/
        ├── icon16.png
        ├── icon48.png
        └── icon128.png
```

### 3.3 Variables de Entorno (`.env.example`)

```ini
# Configuración del Servidor OmniDownloader
HOST=127.0.0.1
PORT=18989
DEBUG=True

# Carpeta de destino de las descargas (por defecto en Downloads/OmniDownloader)
DOWNLOAD_DIR=~/Downloads/OmniDownloader

# Ruta a binario de FFmpeg (dejar vacío si ya está en el PATH del sistema)
FFMPEG_PATH=

# Opciones de concurrencia
MAX_PARALLEL_DOWNLOADS=3
```

### 3.4 API Endpoints (Contrato OpenAPI)

#### 1. `GET /health`

Verifica que el servicio esté online y el estado de los binarios.

- **Respuesta:**
  ```json
  {
    "status": "ok",
    "version": "1.0.0",
    "ffmpeg_available": true,
    "yt_dlp_version": "2024.08.06",
    "download_dir": "C:/Users/MANUEL/Downloads/OmniDownloader"
  }
  ```

#### 2. `POST /api/info`

Obtiene los metadatos de un video o stream antes de descargar.

- **Request Body:**
  ```json
  {
    "url": "https://www.youtube.com/watch?v=example",
    "headers": {
      "User-Agent": "Mozilla/5.0 ...",
      "Referer": "https://www.youtube.com/"
    },
    "cookies": ""
  }
  ```
- **Respuesta Exitosa:**
  ```json
  {
    "id": "example_id",
    "title": "Tutorial Video Marketing",
    "thumbnail": "https://i.ytimg.com/vi/.../maxresdefault.jpg",
    "duration": 420,
    "extractor": "youtube",
    "is_stream": false,
    "formats": [
      {
        "format_id": "best",
        "label": "Mejor calidad disponible (4K/1080p)",
        "resolution": "Original",
        "ext": "mp4"
      },
      {
        "format_id": "1080p",
        "label": "1080p Full HD",
        "resolution": "1920x1080",
        "ext": "mp4"
      },
      {
        "format_id": "720p",
        "label": "720p HD",
        "resolution": "1280x720",
        "ext": "mp4"
      },
      {
        "format_id": "audio_only",
        "label": "Solo Audio (MP3 320k)",
        "resolution": "Audio",
        "ext": "mp3"
      }
    ]
  }
  ```

#### 3. `POST /api/download`

Inicia una descarga en background y devuelve un `task_id`.

- **Request Body:**
  ```json
  {
    "url": "https://example.com/video/master.m3u8",
    "title": "Masterclass Video IA",
    "format_id": "best",
    "quality_profile": "best",
    "headers": {
      "Referer": "https://example.com/course",
      "User-Agent": "Mozilla/5.0 ..."
    },
    "cookies": ""
  }
  ```
- **Respuesta Exitosa:**
  ```json
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "title": "Masterclass Video IA"
  }
  ```

#### 4. `GET /api/progress/{task_id}`

Consulta el estado y progreso en tiempo real de una tarea.

- **Respuesta Exitosa:**
  ```json
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "downloading",
    "progress_percent": 68.4,
    "speed": "12.8 MiB/s",
    "eta_seconds": 15,
    "downloaded_bytes": 142606336,
    "total_bytes": 208500000,
    "filename": "Masterclass Video IA.mp4",
    "file_path": "C:/Users/MANUEL/Downloads/OmniDownloader/Masterclass Video IA.mp4",
    "error": null
  }
  ```
  _(Estados posibles: `queued`, `downloading`, `merging`, `finished`, `error`)_.

#### 5. `GET /api/tasks`

Lista las descargas recientes (activas y completadas).

#### 6. `POST /api/open-folder`

Abre el explorador de Windows resaltando el archivo o la carpeta de descargas.

- **Request Body:**
  ```json
  {
    "file_path": "C:/Users/MANUEL/Downloads/OmniDownloader/Masterclass Video IA.mp4"
  }
  ```

---

## 4. ESPECIFICACIÓN TÉCNICA DE LA EXTENSIÓN CHROME (FRONTEND)

### 4.1 Manifest V3 (`extension/manifest.json`)

```json
{
  "manifest_version": 3,
  "name": "OmniDownloader Pro",
  "version": "1.0.0",
  "description": "Descargador universal de video y audio ilimitado sin marcas de agua.",
  "permissions": ["activeTab", "tabs", "storage", "webRequest"],
  "host_permissions": ["<all_urls>", "http://127.0.0.1:18989/*"],
  "background": {
    "service_worker": "background/service_worker.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content/content_script.js"],
      "run_at": "document_idle"
    }
  ],
  "action": {
    "default_popup": "popup/popup.html",
    "default_title": "OmniDownloader Pro",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

### 4.2 Lógica del Sniffer (`background/service_worker.js`)

- Monitorea `chrome.webRequest.onBeforeRequest` y `onHeadersReceived`.
- Detecta patrones de video:
  - Regex URLs: `/\.(m3u8|mpd|mp4|webm|m4s)(\?|$)/i`
  - Encabezados: `content-type` que comiencen con `video/`, `application/vnd.apple.mpegurl` o `application/dash+xml`.
- Agrupa las URLs por `tabId` y actualiza el badge numérico de la extensión (`chrome.action.setBadgeText`).
- Si el usuario cambia de URL o cierra la pestaña, limpia el cache del `tabId` respectivo.

### 4.3 Interfaz de Usuario del Popup (`popup/`)

- **Diseño visual:** Modo oscuro pulido (Dark Glassmorphism, Tailwind palette `#0f172a`, acentos violeta/azul `#6366f1` y verde esmeralda `#10b981`).
- **Header:**
  - Logo + Nombre "OmniDownloader".
  - Status indicator (Verde si `http://127.0.0.1:18989/health` responde 200; Rojo si no responde, con link a instrucciones de inicio).
- **Cuerpo dinámico:**
  - **Tarjeta 1: Video de la Pestaña Activa.** Si es YouTube, X, Vimeo, Instagram, etc., muestra la miniatura, el título y el selector de calidad:
    - 💎 **Mejor Calidad (Automático 4K/1080p)**
    - 🎬 **1080p Full HD**
    - 📱 **720p HD**
    - 🎵 **Solo Audio (MP3)**
    - Botón de descarga con spinner animado.
  - **Tarjeta 2: Streams Detectados por el Sniffer (HLS / MP4).** Si hay listas de reproducción `.m3u8` detectadas en la página, se listan en un acordeón desplegable con un botón directo "Descargar Stream".
  - **Tarjeta 3: Descargas Activas.** Muestra la barra de progreso en tiempo real (`%`, velocidad en `MB/s`, tiempo restante). Al terminar, muestra el botón "📂 Abrir en Carpeta".

---

## 5. PLAN DE EJECUCIÓN PASO A PASO (ROADMAP 0 A 100)

### Fase 1: Backend Daemon (Python + yt-dlp + FFmpeg)

1. **Configuración y Estructura:** Crear carpetas `server/app/`.
2. **Dependencias:** Crear y congelar `requirements.txt`.
3. **Módulo de Configuración:** `config.py` con resolución dinámica de la carpeta `Downloads` de Windows y detección de binarios.
4. **Módulo Downloader:** `downloader.py` implementando la clase `MediaDownloader` utilizando `yt_dlp.YoutubeDL` con hooks de progreso y mapeo de perfiles de calidad.
5. **Endpoints de API:** `main.py` con CORS habilitado (`*` o extensiones), `/health`, `/api/info`, `/api/download`, `/api/progress/{task_id}`, `/api/tasks`, `/api/open-folder`.
6. **Scripts de Ejecución:** `install.bat` y `start_server.bat`.

### Fase 2: Extensión Chrome (Manifest V3)

1. **Manifest y Permisos:** `extension/manifest.json`.
2. **Background Worker:** `service_worker.js` con sniffer de URLs y gestión de estado por tab.
3. **Content Script:** `content_script.js` para extraer metadatos de la página y elementos multimedia del DOM.
4. **Popup UI:** `popup.html`, `popup.css` y `popup.js` con soporte para selección de calidad, descarga de streams HLS y barra de progreso en vivo.
5. **Generación de Iconos:** Crear los íconos requeridos en 16, 48 y 128px.

### Fase 3: Casos Borde y Pruebas

1. **Prueba de Bypass 403 (Referer/Cookies):** Validar que `yt-dlp` reciba las cabeceras capturadas por el sniffer para evitar rechazos de servidores protegidos.
2. **Muxing de Audio/Video:** Validar que FFmpeg combine correctamente el flujo de video y audio en un único contenedor `.mp4` jugable en cualquier reproductor (VLC, Windows Media Player, etc.).
3. **Pruebas en Múltiples Plataformas:**
   - YouTube (video 1080p+ y solo audio).
   - Twitter / X (video embebido en tweet).
   - Instagram (Reels y videos).
   - Web de cursos con reproductor HLS (`.m3u8`).

---

## 6. DEFINICIÓN DE ÉXITO Y CRITERIOS DE ACEPTACIÓN

El trabajo se considerará 100% completado cuando:

1. `start_server.bat` levante el backend localmente sin arrojar ninguna excepción en consola.
2. La extensión pueda cargarse sin errores de manifest en `chrome://extensions`.
3. Al ingresar a un video en el navegador, el ícono de la extensión muestre el badge numérico y el popup permita disparar la descarga.
4. El archivo final se descargue en `~/Downloads/OmniDownloader/` en alta definición, con audio perfectamente sincronizado, sin marcas de agua y sin esperas artificiales.
