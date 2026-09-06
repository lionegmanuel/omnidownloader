# OmniDownloader Pro 🚀

> **Tu descargador universal de video y audio: ilimitado, privado, sin marcas de agua y de máxima calidad.**
> Funciona con YouTube, Twitter/X, Instagram, TikTok, Facebook, Vimeo, Twitch y cualquier reproductor web con transmisiones HLS (`.m3u8`) o DASH (`.mpd`).

---

## 🎮 ¿Qué es OmniDownloader Pro? (Explicado para todos)

¿Alguna vez quisiste guardar un video de internet o una canción en tu computadora y la página te pedía pagar, te ponía un logo gigante molesto en el medio o te hacía esperar horas?

**¡OmniDownloader Pro soluciona todo eso!**
Es como tener una varita mágica instalada en tu navegador Google Chrome (o Brave o Edge):

1. Detecta automáticamente cualquier video o música que estés viendo en la pantalla.
2. Te deja elegir si lo quieres en **Super Calidad (4K / 1080p)**, en **calidad normal** o **solo el audio en MP3** para escucharlo como música.
3. Lo descarga a máxima velocidad y lo guarda directo en tu computadora.
4. **100% tuyo y privado:** nada pasa por servidores raros en internet; todo funciona seguro dentro de tu propia máquina.

---

## 🧩 ¿Qué necesitas antes de empezar?

Solo necesitas dos cositas que se instalan una sola vez:

1. **Python 3.10 o superior:**
   Si no lo tienes, descárgalo gratis desde [python.org](https://www.python.org/).
   _(¡Muy importante! Cuando lo instales, asegúrate de marcar la casilla que dice **"Add python.exe to PATH"**)_.
2. **FFmpeg:**
   Es el programa mágico que une el audio con el video en alta definición. En Windows se instala abriendo PowerShell y escribiendo:
   ```powershell
   winget install Gyan.FFmpeg
   ```
   _(Si ya lo tienes instalado en tu PC, OmniDownloader lo detectará solo)_.

---

## 🚀 Guía de Uso Paso a Paso (¡Fácil y en 3 minutos!)

### 🏁 Paso 1: Encender el Motor de la Aplicación

Imagina que la aplicación es como un autito a control remoto: para que ande, primero hay que encender el motor.

1. Abre la carpeta del proyecto: `D:\Documents\MANUEL\DEV\video-downloader`.
2. Si es la **primera vez que lo usas**, haz doble clic sobre el archivo:
   ```cmd
   install.bat
   ```
   _(Aparecerá una ventanita verde que instalará todo automáticamente en unos segundos)_.
3. Luego, haz doble clic sobre:
   ```cmd
   start_server.bat
   ```
4. Verás una ventana negra que dice: `Iniciando servidor en http://127.0.0.1:18989...`
   🟢 **¡Listo! El motor ya está encendido.**
   _(⚠️ Deja esta ventanita abierta en tu barra de tareas mientras quieras descargar videos)_.

---

### 🔌 Paso 2: Poner la Extensión en Google Chrome (Se hace una sola vez)

1. Abre tu navegador **Google Chrome** (también sirve Brave o Microsoft Edge).
2. En la barra de direcciones de arriba donde escribes las páginas web, escribe:
   ```text
   chrome://extensions/
   ```
   y presiona `Enter`.
3. Arriba a la derecha, enciende el interruptor que dice **"Modo de desarrollador"** (_Developer mode_).
4. Arriba a la izquierda aparecerá un botón que dice **"Cargar descomprimida"** (_Load unpacked_). Haz clic en él.
5. Se abrirá una ventana para elegir una carpeta. Selecciona la carpeta `extension` ubicada en:
   ```text
   D:\Documents\MANUEL\DEV\video-downloader\extension
   ```
6. Haz clic en **"Seleccionar carpeta"**.
   🎉 **¡Listo!** Verás aparecer a **OmniDownloader Pro** con el ícono del cohete 🚀.
7. Haz clic en el ícono de la pieza de rompecabezas en la barra de Chrome y haz clic en la chincheta (pin) para fijar el cohete siempre visible.

---

### 🎬 Paso 3: ¡A Descargar tu Primer Video o Música!

1. Entra a cualquier página con video: un video de **YouTube**, un reel de **Instagram**, un clip de **TikTok**, un tweet con video en **X/Twitter** o cualquier página de series o cursos.
2. ¡Mira el ícono del cohete 🚀 en tu navegador! Verás que aparece un **numerito verde** que te avisa que ya detectó el video.
3. Haz clic en el cohete 🚀 para abrir la ventanita:
   - Verás la miniatura y el título de lo que estás viendo.
   - Verás una pastilla verde arriba que dice **"Motor Activo"**.
4. En **"Calidad de Descarga"**, elige lo que quieras:
   - 💎 **Mejor Calidad Disponible:** Guarda la resolución más alta (4K, 2K o 1080p a 60 fps).
   - 🎬 **1080p Full HD:** Ideal para ver en la tele o la compu con gran nitidez.
   - 📱 **720p HD:** Archivos más livianos que ocupan poco espacio.
   - 🎵 **Solo Audio (MP3 alta calidad):** Extrae únicamente la música o la voz y la convierte a un archivo `.mp3` para tu celular o reproductor.
5. Haz clic en el gran botón azul: **"⬇️ Descargar Video"**.
6. ¡Mira abajo! Aparecerá una barra de progreso que avanza mostrando el porcentaje, la velocidad de descarga y el tiempo que falta.

---

### 📂 Paso 4: ¿Dónde quedó mi archivo descargado?

¡No tienes que buscarlo a mano!

- Apenas la barra de progreso llega al **100%**, aparecerá un botón que dice **"📂 Abrir"**.
- Haz clic en **"📂 Abrir"** y Windows abrirá la carpeta de tu computadora resaltando exactamente el video que acabas de bajar.
- También puedes hacer clic en **"📂 Abrir Carpeta"** arriba a la derecha en cualquier momento.

Todos tus videos se guardan ordenados en el disco D:

```text
D:\Documents\MANUEL\OmniDownloader\
```

---

## 💡 Trucos y Funciones Pro

- **Descarga con Clic Derecho:** Puedes hacer clic derecho sobre cualquier video o enlace en cualquier página y tocar la opción _"Descargar con OmniDownloader"_. ¡Se descarga al instante sin abrir el popup!
- **Descargar transmisiones directas (HLS / .m3u8):** Si estás en una página que no permite descargar videos fácilmente, abre el acordeón _"Streams Interceptados"_. Verás la lista de transmisiones que el sniffer cazó y podrás tocar el botón de descarga directa de ese stream.
- **Páginas con usuario y contraseña:** Si estás dentro de un curso privado o una plataforma donde iniciaste sesión, OmniDownloader copia automáticamente las cookies de tu sesión para que el servidor no te dé error 403.

---

## ❓ Preguntas Frecuentes (Solución de dudas comunes)

#### 🔴 ¿Por qué la extensión dice "Desconectado" en rojo?

Significa que el motor local está apagado. Solo ve a la carpeta del proyecto y haz doble clic en `start_server.bat`. Vuelve a la extensión y toca el botón _"Reintentar Conexión"_.

#### ⚡ ¿Puedo cerrar la ventana negra del servidor?

Mientras estés usando la computadora para descargar videos, déjala abierta (puedes minimizarla para que no moleste). Cuando ya termines por el día, puedes cerrarla con la cruz `X`.

#### 🎵 ¿Cómo guardo solo las canciones de un video de YouTube?

Antes de tocar el botón de descarga, en el menú desplegable elige la opción **"🎵 Solo Audio (MP3 320 kbps)"**. El sistema descargará el sonido y FFmpeg creará un archivo `.mp3` perfecto y con máxima fidelidad.

#### 🛠️ ¿Cómo cambio la carpeta donde se guardan los videos?

En la carpeta del proyecto hay un archivo llamado `.env`. Puedes abrirlo con el Bloc de notas y cambiar la línea `DOWNLOAD_DIR=` por la carpeta que prefieras (por ejemplo: `DOWNLOAD_DIR=D:/MisVideos`).

---

## 🏗️ Especificaciones Técnicas (Para Desarrolladores)

### Arquitectura

- **Backend:** Python 3.12, FastAPI, Uvicorn, `yt-dlp` (versión 2026.x), `ffmpeg` (con detección automática en PATH o carpeta local `server/bin/`).
- **Frontend:** Google Chrome Extension Manifest V3 (Vanilla JS, CSS3 Dark Glassmorphism, HTML5 nativo, sin frameworks pesados ni pasos de compilación).
- **Concurrencia:** `ThreadPoolExecutor` para descargas asíncronas no bloqueantes y `threading.Lock` para el seguimiento seguro del estado de las tareas.

### Endpoints del Motor Local (`http://127.0.0.1:18989`)

- `GET /health`: Estado del servicio, versión de yt-dlp, presencia de FFmpeg y ruta de descargas.
- `POST /api/info`: Inspección de URL para obtención de títulos, miniaturas, duración y perfiles.
- `POST /api/download`: Encolado y ejecución de descarga en segundo plano (`best`, `1080p`, `720p`, `audio_only`).
- `GET /api/progress/{task_id}`: Polling en tiempo real de porcentaje, velocidad, bytes y ETA.
- `GET /api/tasks`: Historial en memoria de tareas recientes.
- `POST /api/open-folder`: Integración con Windows Shell para abrir o seleccionar archivos en el Explorador.

### Pruebas Automatizadas

Para ejecutar la suite completa de pruebas unitarias e integrales del backend:

```powershell
server\venv\Scripts\pytest -v server\tests\test_api.py
```

_(Resultado actual: 8 pruebas pasando al 100% en menos de 1 segundo)_.

---

## 📝 Registro de Ajustes Técnicos y Validación End-to-End

1. **Resiliencia de Estado en Manifest V3:** Persistencia en `chrome.storage.session` (con fallback a `chrome.storage.local`) para evitar la pérdida de streams interceptados ante la suspensión por inactividad del Service Worker.
2. **Menú Contextual Nativo en Chrome:** Permiso `contextMenus` y registro de acción al clic derecho para descargas directas en segundo plano.
3. **Bypass 403 con Extracción de Cookies:** Captura automática de `document.cookie` desde el content script y remisión en la cabecera `Cookie` de `yt-dlp`.
4. **Muxing y Limpieza de Códigos ANSI:** Configuración de `no_color: True` y limpieza regex de caracteres de terminal para que los datos de progreso y velocidad se muestren limpios en la UI.
5. **Sanitización de Nombres para Windows:** Normalización de caracteres reservados en NTFS (`< > : " / \ | ? *`) con límite seguro de 120 caracteres para evitar errores de ruta en el sistema operativo.
6. **Resolución de Archivo Físico:** Detección en disco del archivo final creado tras el muxing de FFmpeg para alimentar el botón dinámico _"📂 Abrir"_ en la tarjeta de descarga completada.
