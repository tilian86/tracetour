// TraceTour Service Worker — Offline Cache
const CACHE_NAME = 'tracetour-v1';

const CORE_FILES = [
  'index.html',
  'favicon.svg',
];

const AUDIO_FILES = [
  'audio/prologue.mp3','audio/guide.mp3','audio/epilog.mp3',
  'audio/correct.wav','audio/wrong.wav','audio/applause.wav',
  'audio/story_0.mp3','audio/diary_0.mp3','audio/fact_0.mp3','audio/riddle_0.mp3',
  'audio/anecdote_1.mp3',
  'audio/story_2.mp3','audio/diary_2.mp3','audio/fact_2.mp3','audio/riddle_2.mp3',
  'audio/anecdote_3.mp3',
  'audio/story_4.mp3','audio/diary_4.mp3','audio/fact_4.mp3','audio/riddle_4.mp3',
  'audio/anecdote_5.mp3',
  'audio/story_6.mp3','audio/diary_6.mp3','audio/fact_6.mp3','audio/riddle_6.mp3',
  'audio/anecdote_7.mp3',
  'audio/anecdote_8.mp3',
  'audio/story_9.mp3','audio/diary_9.mp3','audio/fact_9.mp3','audio/riddle_9.mp3',
  'audio/anecdote_10.mp3',
  'audio/story_11.mp3','audio/diary_11.mp3','audio/fact_11.mp3','audio/riddle_11.mp3',
  'audio/anecdote_12.mp3',
  'audio/anecdote_13.mp3',
  'audio/story_14.mp3','audio/diary_14.mp3','audio/fact_14.mp3','audio/riddle_14.mp3',
  'audio/anecdote_15.mp3',
  'audio/story_16.mp3','audio/diary_16.mp3','audio/fact_16.mp3','audio/riddle_16.mp3',
];

const IMAGE_FILES = [
  'images/station_0.jpg','images/station_1.jpg','images/station_2.jpg',
  'images/station_3.jpg','images/station_4.jpg','images/station_5.jpg',
  'images/station_6.jpg','images/station_7.jpg','images/station_8.jpg',
  'images/station_9.jpg','images/station_10.jpg','images/station_11.jpg',
  'images/station_12.jpg','images/station_13.jpg','images/station_14.jpg',
  'images/station_15.jpg','images/station_16.jpg',
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

// Cache-first for audio/images, network-first for everything else
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Audio and images: cache-first
  if (url.pathname.match(/\.(mp3|wav|jpg|png|svg)$/)) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(resp => {
          if (resp.ok) {
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

// Listen for download-all message from the app
self.addEventListener('message', event => {
  if (event.data === 'download-all') {
    const allFiles = [...CORE_FILES, ...AUDIO_FILES, ...IMAGE_FILES];
    caches.open(CACHE_NAME).then(cache => {
      const total = allFiles.length;
      let done = 0;
      const dl = file => cache.add(file).then(() => {
        done++;
        // Report progress to all clients
        self.clients.matchAll().then(clients => {
          clients.forEach(c => c.postMessage({ type: 'download-progress', done, total }));
        });
      }).catch(err => {
        done++;
        console.warn('Cache failed:', file, err);
        self.clients.matchAll().then(clients => {
          clients.forEach(c => c.postMessage({ type: 'download-progress', done, total }));
        });
      });
      // Download sequentially to avoid overwhelming the connection
      allFiles.reduce((p, f) => p.then(() => dl(f)), Promise.resolve());
    });
  }
});
