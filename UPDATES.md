# UPDATES — Registro de sesiones de trabajo (OmniDownloader Pro)

Este archivo es el changelog contextual de este repo: cada sesión trabajada se resume acá (qué se hizo, qué se verificó, decisiones relevantes y qué quedó pendiente). Entradas más recientes arriba. Sirve para retomar contexto rápido sin releer el historial completo de conversaciones. **Retención: solo persisten los últimos 3 días de fecha (hoy + 2 días atrás) — al agregar la entrada de una nueva sesión, se elimina toda entrada con más de 2 días de antigüedad respecto a esa fecha** (regla de `CLAUDE.md` sección 5).

---

## 2026-09-09 — Fix de descarga de streams HLS con tokens largos (LMS/coaching.basdonax.com) y robustez del sniffer en el popup

**Pedido de Manuel:** La descarga de una lección de un curso (`coaching.basdonax.com`, plataforma LMS con reproductor JS que sirve HLS con manifest firmado por JWT) fallaba con `Unsupported URL` y, tras el primer fix, con `[Errno 2] No such file or directory` al escribir el `.ytdl` temporal.

**Implementado:**

- `server/app/downloader.py` (`_execute_download_sync`): causa raíz del `[Errno 2]` — el extractor genérico de yt-dlp usaba la URL completa (incluyendo el token JWT en la query string) como `%(id)s`, generando nombres de archivo de cientos de caracteres que sumados a `D:\Documents\MANUEL\OmniDownloader\` superaban el límite de 260 caracteres de Windows. Se reemplazó `%(id)s` por un id corto propio (`task_id[:8]`) en el `outtmpl`, y se agregaron `windowsfilenames: True` y `trim_file_name: 150` como red de seguridad adicional contra rutas largas.
- `extension/popup/popup.js`: el botón principal "Descargar Video" (`handleCurrentDownload`) enviaba la URL de la página del curso en vez del stream sniffeado cuando el usuario descargaba antes de que el reproductor pidiera el manifest `.m3u8` (esto pasa recién al darle Play). Se agregó: (1) refetch de streams sniffeados justo antes de decidir la URL a descargar, en vez de depender del snapshot cargado al abrir el popup; (2) refresco periódico cada 2s de la lista de streams mientras el popup sigue abierto; (3) guard clientside — si el sitio no es una plataforma dedicada (YouTube/Twitter/Instagram/TikTok/etc.) y no hay ningún stream sniffeado, ya no dispara una descarga condenada a `Unsupported URL`, sino que avisa con `alert()` pidiendo reproducir el video primero.

**Verificado:**

- Descarga manual seleccionando el stream `.m3u8` desde la lista del sniffer: funciona end-to-end (extracción, muxing con FFmpeg, archivo final en `D:\Documents\MANUEL\OmniDownloader`).
- Confirmado con `python -c "import yt_dlp; ..."` que `windowsfilenames` y `trim_file_name` son opciones válidas en la versión instalada (yt-dlp 2026.08.19).

**Pendiente real para la próxima sesión:**

- El botón principal "Descargar Video" (el de arriba, no la selección manual del stream) todavía necesita más ajuste/testeo en `coaching.basdonax.com` y sitios LMS similares — Manuel reportó que sigue sin arrancar la descarga correctamente en algunos intentos incluso con el guard nuevo; sospecha de extensión no recargada en `chrome://extensions/` en los intentos fallidos, pero falta confirmar con un log limpio post-reload.
