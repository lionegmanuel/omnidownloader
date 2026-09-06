// OmniDownloader Pro - Popup Logic (Vanilla JS)

const API_BASE = "http://127.0.0.1:18989";

let currentTab = null;
let currentVideoInfo = null;
let currentTabCookies = "";
let currentSniffedStreams = [];
let activePollers = new Map();

document.addEventListener("DOMContentLoaded", async () => {
  initUI();
  await checkServerHealth();
  await loadCurrentTab();
  await loadSniffedStreams();
  await loadRecentTasks();
});

function initUI() {
  document
    .getElementById("btnRetryServer")
    ?.addEventListener("click", checkServerHealth);
  document
    .getElementById("btnDownloadCurrent")
    ?.addEventListener("click", handleCurrentDownload);
  document
    .getElementById("btnOpenFolder")
    ?.addEventListener("click", () => handleOpenFolder());

  // Toggle Acordeón Sniffer
  const toggleSniffer = document.getElementById("toggleSniffer");
  const snifferList = document.getElementById("snifferList");
  const arrow = document.getElementById("snifferArrow");

  toggleSniffer?.addEventListener("click", () => {
    if (snifferList.style.display === "none") {
      snifferList.style.display = "flex";
      arrow.textContent = "▼";
    } else {
      snifferList.style.display = "none";
      arrow.textContent = "▶";
    }
  });

  // Delegación de eventos para botones de abrir archivo en tarjetas de tarea
  const tasksList = document.getElementById("tasksList");
  tasksList?.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn-open-file");
    if (btn) {
      const filePath = decodeURIComponent(btn.getAttribute("data-path") || "");
      handleOpenFolder(filePath);
    }
  });
}

// 1. Chequeo de Salud del Motor Local
async function checkServerHealth() {
  const statusPill = document.getElementById("serverStatus");
  const statusText = document.getElementById("statusText");
  const alertBox = document.getElementById("serverOfflineAlert");

  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      statusPill.className = "status-pill online";
      statusText.textContent = "Motor Activo";
      alertBox.classList.add("hidden");
      return true;
    }
  } catch (err) {
    // Servidor desconectado
  }

  statusPill.className = "status-pill offline";
  statusText.textContent = "Desconectado";
  alertBox.classList.remove("hidden");
  return false;
}

// 2. Obtener Info de la Pestaña Activa
async function loadCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url) return;

  currentTab = tab;

  const videoTitleEl = document.getElementById("videoTitle");
  const platformTag = document.getElementById("platformTag");
  const thumbContainer = document.getElementById("videoThumb");
  const btnDownload = document.getElementById("btnDownloadCurrent");

  const url = tab.url;

  // Páginas internas de Chrome / Navegadores
  if (
    url.startsWith("chrome://") ||
    url.startsWith("edge://") ||
    url.startsWith("brave://") ||
    url.startsWith("about:") ||
    url.startsWith("chrome-extension://")
  ) {
    platformTag.textContent = "Sistema";
    videoTitleEl.textContent = "Pestaña interna del navegador";
    document.getElementById("videoDuration").textContent =
      "Navega a un sitio web con video";
    if (btnDownload) btnDownload.disabled = true;
    return;
  }

  // Detectar plataforma por URL
  let platform = "Web";
  if (url.includes("youtube.com") || url.includes("youtu.be"))
    platform = "YouTube";
  else if (url.includes("twitter.com") || url.includes("x.com"))
    platform = "X / Twitter";
  else if (url.includes("instagram.com")) platform = "Instagram";
  else if (url.includes("tiktok.com")) platform = "TikTok";
  else if (url.includes("vimeo.com")) platform = "Vimeo";
  else if (url.includes("twitch.tv")) platform = "Twitch";
  else if (url.includes("facebook.com")) platform = "Facebook";
  else if (url.includes("reddit.com")) platform = "Reddit";

  platformTag.textContent = platform;
  videoTitleEl.textContent = tab.title || "Video en pestaña";

  // Consultar información del DOM desde el content script (título, poster, cookies)
  try {
    chrome.tabs.sendMessage(tab.id, { action: "GET_DOM_INFO" }, (domInfo) => {
      if (!chrome.runtime.lastError && domInfo) {
        if (domInfo.cookies) {
          currentTabCookies = domInfo.cookies;
        }
        if (domInfo.thumbnail && !thumbContainer.querySelector("img")) {
          thumbContainer.innerHTML = `<img src="${domInfo.thumbnail}" class="thumb-img" alt="Thumbnail" />`;
        }
        if (
          domInfo.title &&
          videoTitleEl.textContent === "Detectando video en la pestaña..."
        ) {
          videoTitleEl.textContent = domInfo.title;
        }
      }
    });
  } catch (_) {}

  // Consultar metadatos enriquecidos al daemon local (FastAPI / yt-dlp)
  try {
    videoTitleEl.title = "Consultando metadatos...";
    const res = await fetch(`${API_BASE}/api/info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: tab.url,
        cookies: currentTabCookies,
        headers: {
          Referer: tab.url,
          "User-Agent": navigator.userAgent,
        },
      }),
    });

    if (res.ok) {
      currentVideoInfo = await res.json();
      if (currentVideoInfo.title) {
        videoTitleEl.textContent = currentVideoInfo.title;
        videoTitleEl.title = currentVideoInfo.title;
      }
      if (currentVideoInfo.duration_string) {
        document.getElementById("videoDuration").textContent =
          `Duración: ${currentVideoInfo.duration_string}`;
      }
      if (currentVideoInfo.thumbnail) {
        thumbContainer.innerHTML = `<img src="${currentVideoInfo.thumbnail}" class="thumb-img" alt="Thumbnail" />`;
      }
    }
  } catch (e) {
    // Si falla /info (por ejemplo, web con reproductor dinámico), mantenemos la info extraída del tab
  }
}

// 3. Cargar Streams Capturados por el Sniffer
async function loadSniffedStreams() {
  if (!currentTab) return;

  chrome.runtime.sendMessage(
    { action: "GET_TAB_STREAMS", tabId: currentTab.id },
    (response) => {
      if (chrome.runtime.lastError || !response || !response.streams) return;

      const streams = response.streams;
      currentSniffedStreams = streams;
      const countBadge = document.getElementById("snifferCountBadge");
      const listEl = document.getElementById("snifferList");

      countBadge.textContent = streams.length.toString();

      if (streams.length === 0) {
        listEl.innerHTML = `<p class="empty-text">No se han detectado transmisiones directas en esta página.</p>`;
        return;
      }

      listEl.innerHTML = "";
      streams.forEach((stream) => {
        const item = document.createElement("div");
        item.className = "stream-item";
        item.innerHTML = `
          <div class="stream-info">
            <span class="stream-type-tag">${stream.type}</span>
            <span class="stream-url" title="${stream.url}">${stream.url}</span>
          </div>
          <div class="stream-actions">
            <button class="btn-icon-action btn-copy" title="Copiar URL">📋</button>
            <button class="btn-icon-action btn-download-stream" title="Descargar este stream">⬇️</button>
          </div>
        `;

        item.querySelector(".btn-copy").addEventListener("click", () => {
          navigator.clipboard.writeText(stream.url);
          item.querySelector(".btn-copy").textContent = "✓";
          setTimeout(
            () => (item.querySelector(".btn-copy").textContent = "📋"),
            1500,
          );
        });

        item
          .querySelector(".btn-download-stream")
          .addEventListener("click", () => {
            const streamTitle = currentTab?.title
              ? `${currentTab.title} [${stream.type}]`
              : `Stream_${stream.type}`;
            triggerDownload(stream.url, streamTitle, "best");
          });

        listEl.appendChild(item);
      });
    },
  );
}

// 4. Disparar Descarga de la Pestaña Activa
async function handleCurrentDownload() {
  if (!currentTab || !currentTab.url) return;

  const btn = document.getElementById("btnDownloadCurrent");
  const btnText = document.getElementById("btnDownloadText");
  const quality = document.getElementById("qualitySelect").value;
  const title = currentVideoInfo?.title || currentTab.title || "Video";

  // Selección inteligente del destino:
  // En plataformas con extractor oficial (YouTube, TikTok, Twitter, Instagram), yt-dlp resuelve la URL de la página.
  // En sitios web de noticias o portales genéricos (TN, Infobae, reproductores JS protegidos por Cloudflare),
  // las páginas arrojan HTTP 400/403 al raspar el HTML. Si el sniffer ya cazó el stream real (.m3u8 o .mp4),
  // lo usamos de forma transparente para que la descarga sea inmediata y sin errores.
  let targetUrl = currentTab.url;
  const isDedicatedPlatform =
    targetUrl.includes("youtube.com") ||
    targetUrl.includes("youtu.be") ||
    targetUrl.includes("twitter.com") ||
    targetUrl.includes("x.com") ||
    targetUrl.includes("instagram.com") ||
    targetUrl.includes("tiktok.com") ||
    targetUrl.includes("vimeo.com") ||
    targetUrl.includes("twitch.tv") ||
    targetUrl.includes("facebook.com") ||
    targetUrl.includes("reddit.com");

  if (
    !isDedicatedPlatform &&
    currentSniffedStreams &&
    currentSniffedStreams.length > 0
  ) {
    const hls = currentSniffedStreams.find(
      (s) => s.type?.includes("HLS") || s.url?.includes(".m3u8"),
    );
    const mp4 = currentSniffedStreams.find(
      (s) => s.type?.includes("MP4") || s.url?.includes(".mp4"),
    );
    const chosen = hls || mp4 || currentSniffedStreams[0];
    if (chosen && chosen.url) {
      targetUrl = chosen.url;
    }
  }

  btn.disabled = true;
  btnText.textContent = "Iniciando descarga...";

  await triggerDownload(targetUrl, title, quality);

  setTimeout(() => {
    btn.disabled = false;
    btnText.textContent = "Descargar Video";
  }, 2000);
}

// Función Universal de Descarga
async function triggerDownload(url, title, qualityProfile) {
  try {
    const res = await fetch(`${API_BASE}/api/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        title: title,
        quality_profile: qualityProfile,
        cookies: currentTabCookies,
        headers: {
          Referer: currentTab?.url || "",
          "User-Agent": navigator.userAgent,
        },
      }),
    });

    if (res.ok) {
      const data = await res.json();
      startTaskPolling(data.task_id, title);
    } else {
      const err = await res.json();
      alert(`Error al iniciar descarga: ${err.detail || "Error desconocido"}`);
    }
  } catch (err) {
    alert(
      "No se pudo conectar con el motor local. ¿Está ejecutándose start_server.bat?",
    );
  }
}

// 5. Polling de Progreso en Tiempo Real
function startTaskPolling(taskId, initialTitle) {
  if (activePollers.has(taskId)) return;

  const pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/progress/${taskId}`);
      if (res.ok) {
        const task = await res.json();
        renderTaskCard(task);

        if (task.status === "finished" || task.status === "error") {
          clearInterval(pollInterval);
          activePollers.delete(taskId);
        }
      }
    } catch (e) {
      // Ignorar errores transitorios de red local
    }
  }, 1000);

  activePollers.set(taskId, pollInterval);
}

// Renderizar o actualizar tarjeta de tarea
function renderTaskCard(task) {
  const listEl = document.getElementById("tasksList");
  const emptyText = document.getElementById("noTasksText");
  if (emptyText) emptyText.style.display = "none";

  let card = document.getElementById(`task-${task.task_id}`);
  if (!card) {
    card = document.createElement("div");
    card.id = `task-${task.task_id}`;
    card.className = "task-item";
    listEl.prepend(card);
  }

  const isFinished = task.status === "finished";
  const isError = task.status === "error";

  let statusLabel = "Descargando...";
  let statusClass = "downloading";
  if (isFinished) {
    statusLabel = "Completado";
    statusClass = "finished";
  } else if (isError) {
    statusLabel = "Error";
    statusClass = "error";
  } else if (task.status === "merging") {
    statusLabel = "Muxing...";
    statusClass = "downloading";
  }

  const pct = task.progress_percent || (isFinished ? 100.0 : 0.0);
  const speed = task.speed || "";
  const eta = task.eta_seconds ? `ETA: ${task.eta_seconds}s` : "";

  let actionHtml = eta;
  if (isFinished) {
    actionHtml = `<button class="btn-text-sm btn-open-file" data-path="${encodeURIComponent(task.file_path || "")}">📂 Abrir</button>`;
  }

  let errorHtml = "";
  if (isError && task.error) {
    errorHtml = `<div class="task-error-msg">${task.error}</div>`;
  }

  card.innerHTML = `
    <div class="task-top">
      <span class="task-title" title="${task.filename || ""}">${task.filename || "Descargando..."}</span>
      <span class="task-status-badge ${statusClass}">${statusLabel}</span>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill ${statusClass}" style="width: ${pct}%"></div>
    </div>
    <div class="task-bottom">
      <span>${pct}% ${speed ? "• " + speed : ""}</span>
      <span>${actionHtml}</span>
    </div>
    ${errorHtml}
  `;
}

// 6. Cargar Tareas Recientes
async function loadRecentTasks() {
  try {
    const res = await fetch(`${API_BASE}/api/tasks`);
    if (res.ok) {
      const tasks = await res.json();
      if (tasks && tasks.length > 0) {
        tasks.forEach((t) => {
          renderTaskCard(t);
          if (
            t.status === "downloading" ||
            t.status === "merging" ||
            t.status === "queued"
          ) {
            startTaskPolling(t.task_id, t.filename);
          }
        });
      }
    }
  } catch (e) {
    // Ignorar si el servidor aún no respondió
  }
}

// 7. Abrir Carpeta o Archivo de Descargas
async function handleOpenFolder(filePath = null) {
  try {
    await fetch(`${API_BASE}/api/open-folder`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: filePath }),
    });
  } catch (e) {
    console.error("Error abriendo carpeta:", e);
  }
}
