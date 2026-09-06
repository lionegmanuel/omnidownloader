// OmniDownloader Pro - Content Script (DOM Inspector)

(function () {
  function scanMedia() {
    const mediaFound = [];
    const seen = new Set();

    function addMedia(url, type) {
      if (!url || typeof url !== "string") return;
      if (url.startsWith("blob:") || url.startsWith("data:")) return;
      if (!seen.has(url)) {
        seen.add(url);
        mediaFound.push({ url, type });
      }
    }

    // 1. Elementos <video> y sus fuentes
    document.querySelectorAll("video").forEach((video) => {
      if (video.src) addMedia(video.src, "HTML5 Video");
      if (video.currentSrc && video.currentSrc !== video.src) {
        addMedia(video.currentSrc, "HTML5 Video Stream");
      }
      video.querySelectorAll("source").forEach((s) => {
        if (s.src) addMedia(s.src, s.type || "HTML5 Video Source");
      });
    });

    // 2. Elementos <audio>
    document.querySelectorAll("audio").forEach((audio) => {
      if (audio.src) addMedia(audio.src, "HTML5 Audio");
      audio.querySelectorAll("source").forEach((s) => {
        if (s.src) addMedia(s.src, s.type || "HTML5 Audio Source");
      });
    });

    // 3. Metadatos OpenGraph / Twitter Card
    const ogVideo =
      document.querySelector('meta[property="og:video"]')?.content ||
      document.querySelector('meta[property="og:video:url"]')?.content ||
      document.querySelector('meta[property="og:video:secure_url"]')?.content ||
      document.querySelector('meta[name="twitter:player:stream"]')?.content;
    if (ogVideo) addMedia(ogVideo, "OpenGraph Video");

    return mediaFound;
  }

  function getPosterThumbnail() {
    const video = document.querySelector("video[poster]");
    if (video && video.poster) return video.poster;
    const ogImage =
      document.querySelector('meta[property="og:image"]')?.content ||
      document.querySelector('meta[name="twitter:image"]')?.content;
    return ogImage || null;
  }

  // Enviar medios descubiertos al Background Service Worker
  try {
    const initialMedia = scanMedia();
    if (initialMedia.length > 0) {
      chrome.runtime
        .sendMessage({
          action: "REGISTER_DOM_MEDIA",
          media: initialMedia,
        })
        .catch(() => {});
    }
  } catch (_) {}

  // Responder a consultas directas del Popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_DOM_INFO") {
      let pageCookies = "";
      try {
        pageCookies = document.cookie || "";
      } catch (_) {}

      sendResponse({
        title: document.title || "Video Web",
        url: window.location.href,
        thumbnail: getPosterThumbnail(),
        cookies: pageCookies,
        media: scanMedia(),
      });
      return false;
    }
  });
})();
