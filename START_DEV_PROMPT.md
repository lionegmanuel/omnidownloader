# PROMPT DE INICIO PARA DESARROLLO END-TO-END (OMNIDOWNLOADER)

> **INSTRUCCIÓN PARA EL DESARROLLADOR / AGENTE:**
> Copia y pega o ejecuta el bloque de prompt que se presenta a continuación para iniciar el desarrollo completo del proyecto de forma 100% autónoma.

```markdown
Eres el Ingeniero de Software Senior Full-Stack asignado para construir de forma autónoma y completa la aplicación "OmniDownloader Pro", una solución privada y sin restricciones para la descarga y procesamiento de videos desde el navegador, superando herramientas como Video DownloadHelper.

Tu misión es desarrollar, integrar y validar la aplicación END-TO-END (de 0 a 100). No tienes asistentes intermedios ni debes delegar tareas: construirás tanto el backend (Python FastAPI + yt-dlp + FFmpeg) como el frontend (Extensión Chrome Manifest V3) y los scripts de automatización.

### DIRECTIVAS DE TRABAJO INNEGOCIABLES:

1. REGLA SUPREMA - EJECUCIÓN CONTINUA SIN FRENARSE (CERO STOPPERS):
   - Trabaja de manera continua e ininterrumpida hasta completar la aplicación al 100%.
   - NO te detengas a pedir confirmaciones, ni a hacer preguntas retóricas, ni a solicitar permiso para crear archivos o instalar dependencias estándar.
   - Si encuentras un error de compilación, sintaxis, dependencias o una incompatibilidad de versión: ANALÍZALO, CORRÍGELO INMEDIATAMENTE y CONTINÚA la marcha.
   - Si surge alguna decisión secundaria de diseño, toma la opción más estándar, moderna y robusta de la industria.
   - Cualquier incidente, detalle técnico o ajuste realizado se documenta ÚNICAMENTE al finalizar la tarea completa en el archivo README.md.

2. FUENTES DE VERDAD TÉCNICA:
   - Antes de escribir cualquier código, lee atentamente los siguientes archivos ya presentes en este repositorio:
     - `CLAUDE.md`: Reglas core de eficiencia, contexto del repo y comandos clave.
     - `TECHNICAL_SPEC_AND_PLAN.md`: Especificación técnica ultra detallada, arquitectura, endpoints REST, esquemas Pydantic y lógica de la extensión.
     - `.env.example`: Configuración de entorno requerida.

3. ALCANCE END-TO-END REQUERIDO:
   Debes implementar y verificar cada uno de los siguientes componentes:

   A) BACKEND LOCAL (Python FastAPI Daemon en `server/`):
   - `server/requirements.txt`: Dependencias congeladas (`fastapi`, `uvicorn`, `yt-dlp`, `pydantic`, `python-dotenv`, `requests`).
   - `server/app/config.py`: Detección automática del directorio de descargas del usuario en Windows (`~/Downloads/OmniDownloader`) y verificación del ejecutable `ffmpeg`.
   - `server/app/models.py`: Modelos Pydantic para `/api/info`, `/api/download`, `/api/progress/{task_id}`, `/api/open-folder`.
   - `server/app/downloader.py`: Integración robusta con `yt-dlp.YoutubeDL` implementando hooks de progreso en tiempo real (porcentaje, velocidad, ETA, tamaño) y soporte para descarga de streams HLS (`.m3u8`) y DASH (`.mpd`) con cabeceras `Referer` y `User-Agent`.
   - `server/app/progress.py`: Almacén en memoria concurrente (`asyncio`/thread-safe) para el seguimiento de descargas activas y completadas.
   - `server/app/utils.py`: Funciones auxiliares de sistema (ej: abrir explorador de Windows en la carpeta de descargas).
   - `server/app/main.py`: Servidor FastAPI con CORS permisivo (`*` o extensiones de Chrome), endpoints `/health`, `/api/info`, `/api/download`, `/api/progress/{task_id}`, `/api/tasks`, `/api/open-folder`.
   - `server/run.py`: Script de arranque directo `python server/run.py` en el puerto `18989`.

   B) EXTENSIÓN CHROME MANIFEST V3 en `extension/`:
   - `extension/manifest.json`: Manifest V3 con permisos `activeTab`, `tabs`, `storage`, `webRequest` y host permissions `<all_urls>`, `http://127.0.0.1:18989/*`.
   - `extension/background/service_worker.js`: Sniffer de red pasivo que detecta URLs multimedia (`.m3u8`, `.mpd`, `.mp4`, `video/*`), mantiene registro por pestaña y actualiza el badge numérico verde en el ícono de la extensión.
   - `extension/content/content_script.js`: Inyector para capturar títulos, miniaturas y elementos `<video>` del DOM.
   - `extension/popup/popup.html`: Interfaz moderna con modo oscuro, status pill (Verde: motor conectado, Rojo: desconectado), tarjeta de video activo con selector de calidad (Mejor calidad, 1080p, 720p, Solo audio MP3), acordeón de streams detectados por el sniffer, y sección de descargas activas con barras de progreso animadas.
   - `extension/popup/popup.css`: Estilos visuales pulidos, responsivos y de alto impacto visual (dark glassmorphism).
   - `extension/popup/popup.js`: Lógica cliente en Vanilla JS, comunicación con el daemon local, polling en tiempo real y disparo de acciones.
   - `extension/icons/`: Iconos en 16x16, 48x48 y 128x128 píxeles.

   C) SCRIPTS DE AUTOMATIZACIÓN PARA WINDOWS:
   - `install.bat`: Crea el entorno virtual `venv`, actualiza `pip` e instala `requirements.txt`.
   - `start_server.bat`: Activa el entorno virtual y ejecuta el servidor local en segundo plano o consola dedicada.

   D) VALIDACIÓN FINAL:
   - Verifica que el servidor Python levante sin errores y que `GET /health` devuelva 200 OK.
   - Verifica que la extensión no tenga advertencias en Chrome.
   - Asegúrate de que el código esté 100% completo, sin TODOs pendientes, y listo para ser probado por el usuario.

Comienza inmediatamente por la lectura de los archivos de especificación y procede a la codificación secuencial hasta dar por finalizado el proyecto.
```
