// OmniDownloader Pro - Background Service Worker (Manifest V3)

const tabStreams = new Map();
const storage = chrome.storage.session || chrome.storage.local;

// Patrones de archivos multimedia y manifests
const MEDIA_REGEX = /\.(m3u8|mpd|mp4|webm|m4v|m4a|mp3)(\?|$)/i;
const HLS_SEGMENT_REGEX = /\.(ts|m4s|aac)(\?|$)/i;

// Inicializar menús contextuales al instalar
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "omnidownloader_download_link",
    title: "Descargar con OmniDownloader",
    contexts: ["video", "audio", "link", "page"],
  });
});

// Manejador del menú contextual
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const targetUrl = info.srcUrl || info.linkUrl || info.pageUrl;
  if (!targetUrl) return;

  try {
    const res = await fetch("http://127.0.0.1:18989/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: targetUrl,
        title: tab?.title || "Descarga Directa",
        quality_profile: "best",
        headers: {
          Referer: tab?.url || "",
          "User-Agent": navigator.userAgent,
        },
      }),
    });
    if (res.ok && tab?.id) {
      chrome.action.setBadgeText({ tabId: tab.id, text: "OK" });
      chrome.action.setBadgeBackgroundColor({
        tabId: tab.id,
        color: "#10B981",
      });
      setTimeout(() => updateBadgeFromStorage(tab.id), 2500);
    }
  } catch (err) {
    console.warn("[OmniDownloader] Motor local no disponible:", err);
    if (tab?.id) {
      chrome.action.setBadgeText({ tabId: tab.id, text: "ERR" });
      chrome.action.setBadgeBackgroundColor({
        tabId: tab.id,
        color: "#EF4444",
      });
      setTimeout(() => updateBadgeFromStorage(tab.id), 2500);
    }
  }
});

// Interceptar peticiones de red
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const { tabId, url } = details;
    if (tabId < 0 || !url) return;

    // Ignorar requests locales a nuestro propio daemon
    if (url.includes("127.0.0.1:18989") || url.includes("localhost:18989"))
      return;

    // Filtrar segmentos individuales para no saturar si ya capturamos la lista
    if (HLS_SEGMENT_REGEX.test(url)) return;

    if (MEDIA_REGEX.test(url)) {
      let type = "MP4";
      if (url.includes(".m3u8")) type = "HLS (.m3u8)";
      else if (url.includes(".mpd")) type = "DASH (.mpd)";
      else if (url.includes(".webm")) type = "WEBM";
      else if (url.includes(".mp3") || url.includes(".m4a")) type = "AUDIO";

      addStreamToTab(tabId, {
        url: url,
        type: type,
        initiator: details.initiator || "",
      });
    }
  },
  { urls: ["<all_urls>"] },
);

// Interceptar encabezados de respuesta para tipos MIME de video
chrome.webRequest.onHeadersReceived.addListener(
  (details) => {
    const { tabId, url, responseHeaders } = details;
    if (tabId < 0 || !url) return;
    if (url.includes("127.0.0.1:18989") || url.includes("localhost:18989"))
      return;

    const contentTypeHeader = responseHeaders?.find(
      (h) => h.name.toLowerCase() === "content-type",
    );

    if (contentTypeHeader && contentTypeHeader.value) {
      const ct = contentTypeHeader.value.toLowerCase();
      let type = null;

      if (
        ct.includes("application/vnd.apple.mpegurl") ||
        ct.includes("application/x-mpegurl")
      ) {
        type = "HLS (.m3u8)";
      } else if (ct.includes("application/dash+xml")) {
        type = "DASH (.mpd)";
      } else if (ct.startsWith("video/") && !HLS_SEGMENT_REGEX.test(url)) {
        type = ct.split("/")[1]?.toUpperCase() || "VIDEO";
      } else if (ct.startsWith("audio/")) {
        type = "AUDIO (" + (ct.split("/")[1]?.toUpperCase() || "STREAM") + ")";
      }

      if (type) {
        addStreamToTab(tabId, {
          url: url,
          type: type,
          initiator: details.initiator || "",
        });
      }
    }
  },
  { urls: ["<all_urls>"] },
  ["responseHeaders"],
);

async function getStreamsForTab(tabId) {
  if (tabStreams.has(tabId)) {
    return tabStreams.get(tabId);
  }
  const key = `tab_streams_${tabId}`;
  const data = await storage.get(key);
  const list = data[key] || [];
  tabStreams.set(tabId, list);
  return list;
}

async function addStreamToTab(tabId, streamData) {
  const list = await getStreamsForTab(tabId);

  // Evitar duplicados por URL exacta
  if (!list.some((item) => item.url === streamData.url)) {
    list.push({
      ...streamData,
      id: Date.now() + Math.random().toString(36).substring(2, 6),
      timestamp: Date.now(),
    });

    tabStreams.set(tabId, list);
    const key = `tab_streams_${tabId}`;
    await storage.set({ [key]: list });
    updateBadge(tabId, list.length);
  }
}

async function updateBadgeFromStorage(tabId) {
  const list = await getStreamsForTab(tabId);
  updateBadge(tabId, list.length);
}

function updateBadge(tabId, count) {
  if (count > 0) {
    chrome.action.setBadgeText({ tabId, text: count.toString() });
    chrome.action.setBadgeBackgroundColor({ tabId, color: "#10B981" }); // Verde esmeralda
  } else {
    chrome.action.setBadgeText({ tabId, text: "" });
  }
}

// Limpiar memoria y almacenamiento cuando la pestaña cambia de URL o se cierra
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    tabStreams.delete(tabId);
    await storage.remove(`tab_streams_${tabId}`);
    updateBadge(tabId, 0);
  }
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  tabStreams.delete(tabId);
  await storage.remove(`tab_streams_${tabId}`);
});

// Canal de mensajes con Popup y Content Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "GET_TAB_STREAMS") {
    const tabId = request.tabId;
    getStreamsForTab(tabId).then((streams) => {
      sendResponse({ streams: streams || [] });
    });
    return true; // Asíncrono
  }

  if (request.action === "REGISTER_DOM_MEDIA") {
    const tabId = sender.tab?.id;
    if (tabId && request.media && Array.isArray(request.media)) {
      request.media.forEach((item) => {
        if (item.url) {
          addStreamToTab(tabId, {
            url: item.url,
            type: item.type || "HTML5 Video",
            initiator: sender.tab.url || "",
          });
        }
      });
    }
    sendResponse({ success: true });
    return false;
  }
});
