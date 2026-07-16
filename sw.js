// TraceTour Service Worker — Offline Cache
const CACHE_NAME = 'tracetour-v4';

const CORE_FILES = [
  'index.html',
  'app.html',
  'favicon.svg',
  'fonts/fonts.css',
  'css/tailwind.css',
];

// Leaflet vom CDN — wird beim Offline-Download mitgecacht, sonst ist die Karte offline kaputt
const CDN_FILES = [
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
];

// Sound-Effekte + sprachneutrale Dateien (liegen nur in audio/)
const SFX_FILES = [
  'audio/correct.wav', 'audio/wrong.wav', 'audio/applause.mp3', 'audio/fanfare.wav',
];

// Sprachabhängige Audio-Dateien (Basename); Präfix 'audio/' (DE) bzw. 'audio/en/' (EN)
const AUDIO_BASENAMES = [
  'prologue.mp3', 'guide.mp3', 'epilog.mp3', 'formula.mp3', 'thanks.mp3',
  'bonus_8.mp3', 'bonus_13.mp3', 'bonus_16.mp3',
  'story_0.mp3', 'diary_0.mp3', 'fact_0.mp3', 'riddle_0.mp3',
  'anecdote_1.mp3',
  'story_2.mp3', 'diary_2.mp3', 'fact_2.mp3', 'riddle_2.mp3',
  'anecdote_3.mp3',
  'story_4.mp3', 'diary_4.mp3', 'fact_4.mp3', 'riddle_4.mp3',
  'anecdote_5.mp3',
  'story_6.mp3', 'diary_6.mp3', 'fact_6.mp3', 'riddle_6.mp3',
  'anecdote_7.mp3',
  'anecdote_8.mp3',
  'story_9.mp3', 'diary_9.mp3', 'fact_9.mp3', 'riddle_9.mp3',
  'anecdote_10.mp3',
  'story_11.mp3', 'diary_11.mp3', 'fact_11.mp3', 'riddle_11.mp3',
  'anecdote_12.mp3',
  'anecdote_13.mp3',
  'story_14.mp3', 'diary_14.mp3', 'fact_14.mp3', 'riddle_14.mp3',
  'anecdote_15.mp3',
  'story_16.mp3', 'diary_16.mp3', 'fact_16.mp3', 'riddle_16.mp3',
];

const IMAGE_FILES = [
  'images/station_0.jpg', 'images/station_1.jpg', 'images/station_2.jpg',
  'images/station_3.jpg', 'images/station_4.jpg', 'images/station_5.jpg',
  'images/station_6.jpg', 'images/station_7.jpg', 'images/station_8.jpg',
  'images/station_9.jpg', 'images/station_10.jpg', 'images/station_11.jpg',
  'images/station_12.jpg', 'images/station_13.jpg', 'images/station_14.jpg',
  'images/station_15.jpg', 'images/station_16.jpg',
  'images/hero_neckarfront.jpg',
];

// Only cache core files on install — audio/images cached on demand or explicit download
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_FILES))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Cache-first for audio/images/CDN assets, network-first for everything else
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  const isCdnAsset = url.hostname === 'unpkg.com';

  // Audio, images, Leaflet: cache-first
  if (isCdnAsset || url.pathname.match(/\.(mp3|wav|jpg|png|svg|css|woff2)$/)) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(resp => {
          if (resp.ok || resp.type === 'opaque') {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return resp;
        });
      })
    );
    return;
  }

  // HTML/JS: network-first with cache fallback
  if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('.js')) {
    event.respondWith(
      fetch(event.request).then(resp => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return resp;
      }).catch(() => caches.match(event.request))
    );
    return;
  }

  // Everything else: network with cache fallback
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

// Listen for download-all message from the app.
// Accepts legacy string 'download-all' (= DE) or { type: 'download-all', lang: 'de'|'en' }.
self.addEventListener('message', event => {
  const msg = event.data;
  const isDownload = msg === 'download-all' || (msg && msg.type === 'download-all');
  if (!isDownload) return;

  const lang = (msg && msg.lang) === 'en' ? 'en' : 'de';
  const audioPrefix = lang === 'en' ? 'audio/en/' : 'audio/';
  const audioFiles = AUDIO_BASENAMES.map(f => audioPrefix + f);
  const allFiles = [...CORE_FILES, ...CDN_FILES, ...SFX_FILES, ...audioFiles, ...IMAGE_FILES];

  caches.open(CACHE_NAME).then(cache => {
    const total = allFiles.length;
    let done = 0;
    const report = () => self.clients.matchAll().then(clients => {
      clients.forEach(c => c.postMessage({ type: 'download-progress', done, total }));
    });
    const dl = file => cache.add(new Request(file, { mode: file.startsWith('http') ? 'no-cors' : 'same-origin' }))
      .then(() => { done++; report(); })
      .catch(err => { done++; console.warn('Cache failed:', file, err); report(); });
    // Download sequentially to avoid overwhelming the connection
    allFiles.reduce((p, f) => p.then(() => dl(f)), Promise.resolve());
  });
});
