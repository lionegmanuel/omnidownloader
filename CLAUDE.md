# OmniDownloader — CLAUDE.md

## Reglas Core — Ahorro Máximo de Tokens & Eficiencia Absoluta

### 1. Contexto y lectura

- Antes de escribir código: inspeccionar los archivos existentes (`server/` y `extension/`).
- Leer sólo lo estrictamente necesario (`offset`/`limit` o rangos específicos).
- Si la ruta exacta ya se conoce, leer directo sin pasos intermedios innecesarios.
- No releer archivos ya leídos en la sesión salvo que hayan sido modificados.
- Paralelizar llamadas independientes siempre que sea posible.

### 2. Edición de código

- Ediciones quirúrgicas sobre reescrituras masivas.
- Cambiar sólo lo necesario sin reformatear archivos ajenos.
- Soluciones minimalistas, robustas y de calidad de producción: cero abstracciones prematuras.
- Código limpio, tipado en Python (Pydantic / Type Hints) y JavaScript moderno (ES6+ sin frameworks pesados en la extensión para máxima velocidad y cero build step).
- **Almacenamiento exclusivo en disco D:** Todas las descargas multimedia y archivos generados deben guardarse estrictamente en la unidad `D:` (por defecto: `D:\Documents\MANUEL\OmniDownloader`), NUNCA en la unidad `C:`.

### 3. Comunicación (Cero Fluff)

- Respuestas directas, técnicas y concisas. Sin preámbulos aduladores ni recap redundante.
- No narrar el plan antes de ejecutar — ejecutar directamente.
- Si surge un ajuste menor, resolverlo inmediatamente sin interrumpir la ejecución.

### 4. REGLA SUPREMA: EJECUCIÓN CONTINUA SIN FRENARSE (CERO STOPPERS)

- **El desarrollo de esta aplicación debe realizarse y completarse END-TO-END de punta a punta.**
- **Bajo ninguna circunstancia detenerse a pedir confirmación por errores menores de compilación, sintaxis o dependencias:** el agente/dev debe leer el error, corregirlo y seguir adelante de inmediato.
- Si existe alguna discrepancia o alternativa técnica, tomar la decisión más robusta y estándar de la industria de forma autónoma.
- **Cualquier detalle, advertencia menor o notas de arquitectura se documenta ÚNICAMENTE al finalizar todo el trabajo.**

### 5. Registro de Sesiones en `UPDATES.md` (Política de Retención de 3 Días)

- **Propósito:** `UPDATES.md` es el changelog contextual obligatorio de este repositorio. Resume al final de cada sesión de trabajo qué se hizo, qué se verificó, qué decisiones de arquitectura se tomaron y qué quedó pendiente.
- **Ubicación:** En la raíz del repositorio (`UPDATES.md`).
- **Regla Estricta de Retención para Ahorro de Tokens:** Solo persisten los últimos 3 días de fecha trabajados (hoy + 2 días anteriores). Al redactar la entrada de una nueva sesión, se elimina toda entrada con más de 2 días de antigüedad respecto a la fecha de esa sesión.
- **Estructura fija por entrada:**
  1. Título con fecha: `## YYYY-MM-DD — <Título del hito>`
  2. `**Pedido de Manuel:**` resumen del requerimiento.
  3. `**Implementado:**` módulos modificados/creados y decisiones técnicas tomadas.
  4. `**Verificado:**` comandos de tests (`pytest`, `curl`, comprobaciones reales) y resultados.
  5. `**Pendiente real para la próxima sesión:**` próximos pasos para retomar de inmediato.

---

## Contexto del Proyecto

**Nombre:** OmniDownloader Pro
**Ubicación:** `D:\Documents\MANUEL\DEV\video-downloader`
**Propósito:** Solución privada, potente y sin límites para descarga y procesamiento de video/audio desde navegadores basados en Chromium. Supera a herramientas como Video DownloadHelper al eliminar marcas de agua, límites de tiempo, cuotas de pago y restricciones de plataformas (soporta YouTube, X/Twitter, Instagram, TikTok, HLS `.m3u8`, DASH `.mpd`, y cualquier reproductor web).

---

## Arquitectura del Repositorio

El proyecto se divide estrictamente en dos partes desacopladas:

1. **`server/` (Backend / Local Engine):**
   - **Tecnología:** Python 3.10+, FastAPI, Uvicorn, `yt-dlp`, `ffmpeg`.
   - **Puerto local:** `http://127.0.0.1:18989`
   - **Rol:** Recibe URLs y cabeceras (`Referer`, `Cookies`), extrae metadatos en milisegundos, ejecuta descargas multihilo a máxima velocidad, combina pistas de audio/video en 4K/60fps con FFmpeg y deposita los archivos en la carpeta de descargas del usuario.

2. **`extension/` (Frontend / Browser Sniffer):**
   - **Tecnología:** Chrome Extension Manifest V3 (HTML5, Modern CSS, Vanilla JS).
   - **Rol:**
     - Detecta la pestaña actual y el tipo de plataforma.
     - Sniffer de red pasivo (`webRequest`) que caza archivos multimedia (`.m3u8`, `.mpd`, `.mp4`).
     - Muestra un badge con el conteo de videos disponibles.
     - Popup moderno (Glassmorphism dark theme) con selector de calidad (Mejor calidad, 1080p, 720p, Solo Audio MP3), lista de streams detectados y barra de progreso en vivo.

---

## Estructura de Directorios

```
video-downloader/
├── CLAUDE.md                    # Este archivo de directivas y contexto
├── TECHNICAL_SPEC_AND_PLAN.md   # Especificación técnica ultra detallada 0 a 100
├── START_DEV_PROMPT.md          # Prompt de inicio para ejecución autónoma
├── .env.example                 # Variables de entorno modelo
├── .gitignore                   # Exclusiones de Git
├── README.md                    # Manual de usuario y troubleshooting
├── install.bat                  # Script de instalación Windows 1-click
├── start_server.bat             # Script de inicio del backend
│
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Entrypoint FastAPI y CORS
│   │   ├── config.py            # Configuración y rutas
│   │   ├── models.py            # Esquemas Pydantic
│   │   ├── downloader.py        # Wrapper asíncrono sobre yt-dlp
│   │   ├── progress.py          # Gestor de tareas y estado en memoria
│   │   └── utils.py             # Utilidades de sistema y FFmpeg detection
│   ├── bin/                     # Directorio local opcional para ffmpeg.exe
│   ├── requirements.txt         # Dependencias pip
│   └── run.py                   # Script de inicio directo
│
└── extension/
    ├── manifest.json            # Manifest V3
    ├── background/
    │   └── service_worker.js    # Sniffer de peticiones de red
    ├── content/
    │   └── content_script.js    # Inspector de medios en el DOM
    ├── popup/
    │   ├── popup.html           # Interfaz de usuario
    │   ├── popup.css            # Estilos dark mode
    │   └── popup.js             # Lógica cliente y polling de progreso
    └── icons/                   # Íconos de la extensión (16, 48, 128 px)
```

---

## Comandos Operativos Clave

### 1. Backend (Servidor Local)

- **Instalación de dependencias (Windows):**

  ```cmd
  python -m venv server\venv
  server\venv\Scripts\pip install -r server\requirements.txt
  ```

  _O simplemente ejecutar:_ `install.bat`

- **Iniciar el servidor:**

  ```cmd
  server\venv\Scripts\python server\run.py
  ```

  _O simplemente ejecutar:_ `start_server.bat`

- **Verificar salud del servidor:**
  Navegar a `http://127.0.0.1:18989/health` o ejecutar:
  ```powershell
  curl http://127.0.0.1:18989/health
  ```

### 2. Extensión Chrome

- Cargar en el navegador:
  1. Abrir `chrome://extensions/`
  2. Activar switch **"Modo de desarrollador"** (arriba a la derecha).
  3. Clic en **"Cargar descomprimida"** (_Load unpacked_).
  4. Seleccionar el directorio `D:\Documents\MANUEL\DEV\video-downloader\extension`.

---

## Contrato de API Local

- `GET /health`: Estado del servicio, versión de `yt-dlp` y presencia de `ffmpeg`.
- `POST /api/info`: Metadatos del video (`{ "url": "..." }`). Retorna título, thumbnail, duración y formatos.
- `POST /api/download`: Dispara descarga asíncrona (`{ "url": "...", "quality_profile": "best|1080p|720p|audio_only" }`). Retorna `task_id`.
- `GET /api/progress/{task_id}`: Estado, `%`, velocidad (`MB/s`), tiempo restante y path final.
- `GET /api/tasks`: Lista de tareas recientes.
- `POST /api/open-folder`: Abre el explorador de Windows en la carpeta de descargas con el archivo seleccionado.

---

## Criterios de Calidad Innegociables

1. **Sin dependencias de compilación para la extensión:** HTML/JS/CSS nativo para permitir carga instantánea en Chrome sin requerir `npm build` o webpack.
2. **Resiliencia ante errores 403:** El sniffer de la extensión debe pasar cabeceras (`Referer` y `User-Agent`) al backend para saltar las protecciones anti-hotlink de plataformas privadas.
3. **Muxing limpio:** Siempre combinar con FFmpeg copiando codecs (`-c copy`) cuando sea posible para no perder calidad ni sobrecargar la CPU.
