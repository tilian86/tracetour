// TraceTour Service Worker — Offline-Cache
//
// Zwei Caches:
//  - CORE:  Seiten, CSS, JS, Schriften. Bei jeder Änderung an CORE_FILES/ASSET_V hochzählen.
//  - MEDIA: Audios und Bilder (groß, ändern sich selten). Bleibt über Code-Updates erhalten,
//           damit ein Update niemandem mitten in der Tour die Offline-Audios löscht.
//           Nur hochzählen, wenn MP3s oder Fotos unter gleichem Dateinamen ersetzt wurden.
const CORE_CACHE = 'tracetour-core-v5';
const MEDIA_CACHE = 'tracetour-media-v1';
const ASSET_V = '20261026'; // muss zu den ?v=-Parametern in den HTML-Dateien passen
const NET_TIMEOUT = 4000;   // ms: danach liefern Seiten bei schlechtem Netz die gespeicherte Version

const CORE_FILES = [
  'index.html',
  'app.html',
  'kinder.html',
  'favicon.svg',
  'fonts/fonts.css?v=' + ASSET_V,
  'css/tailwind.css?v=' + ASSET_V,
  'fonts/materialsymbols-subset.woff2?v=1',
  'vendor/leaflet/leaflet.css?v=1.9.4',
  'vendor/leaflet/leaflet.js?v=1.9.4',
];

const FONT_FILES = [
  'fonts/epilogue-O4ZRFGj5hxF0EhjimlIksgg4lWmc.woff2',
  'fonts/epilogue-O4ZRFGj5hxF0EhjimlIqsgg4lWmc8kI.woff2',
  'fonts/inter-UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2',
  'fonts/inter-UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7W0Q5n-wU.woff2',
  'fonts/jetbrainsmono-tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTNFOVk6OThhvAWV8.woff2',
  'fonts/jetbrainsmono-tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOVk6OThhvA.woff2',
  'fonts/montserrat-JTUSjIg1_i6t8kCHKm459WdhyyTh89ZNpQ.woff2',
  'fonts/montserrat-JTUSjIg1_i6t8kCHKm459WlhyyTh89Y.woff2',
];
const KIDS_FONT_FILES = [
  'fonts/nunito-XRXV3I6Li01BKofINeaBTMnFcQ.woff2',
  'fonts/nunito-XRXV3I6Li01BKofIO-aBTMnFcQIG.woff2',
];

// Sound-Effekte (sprachneutral, liegen nur in audio/)
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
// audio/en/thanks.mp3 existiert noch nicht (App blendet die Zeile dann aus)
const AUDIO_MISSING_EN = ['thanks.mp3'];

const IMAGE_FILES = [
  'images/station_0.jpg', 'images/station_1.jpg', 'images/station_2.jpg',
  'images/station_3.jpg', 'images/station_4.jpg', 'images/station_5.jpg',
  'images/station_6.jpg', 'images/station_7.jpg', 'images/station_8.jpg',
  'images/station_9.jpg', 'images/station_10.jpg', 'images/station_11.jpg',
  'images/station_12.jpg', 'images/station_13.jpg', 'images/station_14.jpg',
  'images/station_15.jpg', 'images/station_16.jpg',
  'images/hero_neckarfront.jpg', 'images/city_tuebingen2.jpg', 'images/tour_kinder.jpg',
  'images/trace-avatar.png', 'images/favicon-32.png',
];

const KIDS_FILES = [
  'audio/kinder/prolog.mp3',
  'audio/kinder/story_0.mp3', 'audio/kinder/story_1.mp3', 'audio/kinder/story_2.mp3',
  'audio/kinder/story_3.mp3', 'audio/kinder/story_4.mp3', 'audio/kinder/story_5.mp3',
  'audio/kinder/story_6.mp3', 'audio/kinder/story_7.mp3',
  'images/kinder/station_0.jpg', 'images/kinder/station_1.jpg', 'images/kinder/station_1b.jpg',
  'images/kinder/station_2.jpg', 'images/kinder/station_3.jpg', 'images/kinder/station_4.jpg',
  'images/kinder/station_5.jpg', 'images/kinder/station_6.jpg', 'images/kinder/station_7.jpg',
  'images/favicon-32.png',
];

const MEDIA_RE = /\.(mp3|wav|jpg|jpeg|png|svg|webp)$/i;
const ASSET_RE = /\.(css|js|woff2)$/i;

self.addEventListener('install', event => {
  // Einzeln cachen: eine fehlende Datei soll die Installation nicht scheitern lassen
  event.waitUntil(
    caches.open(CORE_CACHE)
      .then(cache => Promise.all(CORE_FILES.map(f => cache.add(f).catch(() => {}))))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keep = [CORE_CACHE, MEDIA_CACHE];
    for (const key of await caches.keys()) {
      if (keep.includes(key)) continue;
      // Altes Einheits-Cache (tracetour-v1…v4): heruntergeladene Audios/Bilder übernehmen
      if (/^tracetour-v\d+$/.test(key)) await migrateMedia(key);
      await caches.delete(key);
    }
    await self.clients.claim();
  })());
});

async function migrateMedia(oldKey) {
  try {
    const old = await caches.open(oldKey);
    const media = await caches.open(MEDIA_CACHE);
    for (const req of await old.keys()) {
      const url = new URL(req.url);
      if (url.origin !== self.location.origin || !MEDIA_RE.test(url.pathname)) continue;
      const resp = await old.match(req);
      if (resp && resp.status === 200) await media.put(url.href, resp);
    }
  } catch (e) {}
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Kartenkacheln, Routing, Code-Prüfung usw. gehen direkt ans Netz
  if (url.origin !== self.location.origin) return;
  const path = url.pathname;

  if (MEDIA_RE.test(path)) {
    event.respondWith(mediaFirst(req));
  } else if (ASSET_RE.test(path) && !path.endsWith('/sw.js')) {
    event.respondWith(staleWhileRevalidate(event, req));
  } else if (req.mode === 'navigate' || path.endsWith('.html') || path.endsWith('/')) {
    event.respondWith(networkFirst(req));
  }
});

// Audios/Bilder: erst Cache, dann Netz. Audio-Player fragen per Range-Header nach
// Teilstücken — Safari spielt Audio aus dem Cache nur mit echter 206-Antwort ab.
async function mediaFirst(req) {
  const cache = await caches.open(MEDIA_CACHE);
  const range = req.headers.get('range');
  const cached = await cache.match(req.url);
  if (cached) return range ? rangeResponse(cached, range) : cached;
  try {
    const resp = await fetch(req);
    if (!range && resp.status === 200 && resp.type === 'basic') {
      cache.put(req.url, resp.clone()).catch(() => {});
    }
    return resp;
  } catch (e) {
    return new Response('', { status: 504, statusText: 'Offline' });
  }
}

async function rangeResponse(resp, range) {
  const blob = await resp.blob();
  const size = blob.size;
  const type = resp.headers.get('Content-Type') || 'application/octet-stream';
  const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  if (!m || (m[1] === '' && m[2] === '')) {
    return new Response(blob, { status: 200, headers: { 'Content-Type': type, 'Content-Length': String(size), 'Accept-Ranges': 'bytes' } });
  }
  let start, end;
  if (m[1] === '') { start = Math.max(0, size - Number(m[2])); end = size - 1; }
  else { start = Number(m[1]); end = m[2] === '' ? size - 1 : Math.min(Number(m[2]), size - 1); }
  if (start >= size || start > end) {
    return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
  }
  const part = blob.slice(start, end + 1);
  return new Response(part, {
    status: 206,
    statusText: 'Partial Content',
    headers: { 'Content-Type': type, 'Content-Range': `bytes ${start}-${end}/${size}`, 'Content-Length': String(part.size), 'Accept-Ranges': 'bytes' },
  });
}

// CSS/JS/Schriften: sofort aus dem Cache, im Hintergrund aktualisieren
async function staleWhileRevalidate(event, req) {
  const cache = await caches.open(CORE_CACHE);
  const cached = await cache.match(req);
  const net = fetch(req).then(resp => {
    if (resp.ok && resp.type === 'basic') cache.put(req, resp.clone()).catch(() => {});
    return resp;
  });
  if (cached) {
    event.waitUntil(net.catch(() => {}));
    return cached;
  }
  try {
    return await net;
  } catch (e) {
    // Offline und genau diese Version fehlt: irgendeine gespeicherte Version ist besser als nichts
    return (await cache.match(req, { ignoreSearch: true })) || Response.error();
  }
}

// Seiten: Netz zuerst. Bei schlechtem Netz nach NET_TIMEOUT die gespeicherte Version.
async function networkFirst(req) {
  const cache = await caches.open(CORE_CACHE);
  const net = fetch(req).then(resp => {
    if (resp.ok && resp.type === 'basic') cache.put(pageKey(req.url), resp.clone()).catch(() => {});
    return resp;
  });
  net.catch(() => {});
  const timeout = new Promise(resolve => setTimeout(resolve, NET_TIMEOUT, 'timeout'));
  try {
    const first = await Promise.race([net, timeout]);
    if (first !== 'timeout') return first;
    return (await cache.match(pageKey(req.url))) || await net;
  } catch (e) {
    return (await cache.match(pageKey(req.url))) || offlinePage();
  }
}

function pageKey(href) {
  const url = new URL(href);
  const path = url.pathname.endsWith('/') ? url.pathname + 'index.html' : url.pathname;
  return url.origin + path;
}

function offlinePage() {
  const html = '<!DOCTYPE html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    + '<title>Offline – TraceTour</title><body style="font-family:-apple-system,sans-serif;background:#1e293b;color:#d2e4fb;text-align:center;padding:3rem 1.5rem">'
    + '<h1 style="font-size:1.4rem">Gerade kein Netz 📶</h1><p>Diese Seite ist noch nicht offline gespeichert. Sobald du wieder Empfang hast, geht es weiter.</p>'
    + '<p style="color:#a3b3c7">No connection right now. This page has not been saved for offline use yet.</p>'
    + '<p><a href="" style="color:#ffb59c">Nochmal versuchen / Try again</a></p></body></html>';
  return new Response(html, { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

// Download für unterwegs. Nachricht: { type: 'download-all', lang: 'de'|'en', tour: 'adult'|'kids' }
// (alte Form 'download-all' = Erwachsenen-Tour auf Deutsch)
const running = {};
self.addEventListener('message', event => {
  const msg = event.data;
  const isDownload = msg === 'download-all' || (msg && msg.type === 'download-all');
  if (!isDownload) return;
  const tour = (msg && msg.tour) === 'kids' ? 'kids' : 'adult';
  const lang = (msg && msg.lang) === 'en' ? 'en' : 'de';
  const job = tour + '-' + lang;
  if (running[job]) return;
  running[job] = downloadAll(tour, lang).finally(() => { delete running[job]; });
  event.waitUntil(running[job]);
});

async function downloadAll(tour, lang) {
  let files;
  if (tour === 'kids') {
    files = [...CORE_FILES, ...KIDS_FONT_FILES, ...SFX_FILES, ...KIDS_FILES];
  } else {
    const prefix = lang === 'en' ? 'audio/en/' : 'audio/';
    const audio = AUDIO_BASENAMES
      .filter(f => !(lang === 'en' && AUDIO_MISSING_EN.includes(f)))
      .map(f => prefix + f);
    files = [...CORE_FILES, ...FONT_FILES, ...SFX_FILES, ...audio, ...IMAGE_FILES];
  }
  const core = await caches.open(CORE_CACHE);
  const media = await caches.open(MEDIA_CACHE);
  const total = files.length;
  let done = 0, failed = 0;
  const report = async () => {
    const clients = await self.clients.matchAll({ includeUncontrolled: true, type: 'window' });
    clients.forEach(c => c.postMessage({ type: 'download-progress', tour, done, total, failed }));
  };
  // Nacheinander laden, damit eine schwache Verbindung nicht überlastet wird
  for (const file of files) {
    const url = new URL(file, self.registration.scope).href;
    const isMedia = MEDIA_RE.test(new URL(url).pathname);
    const cache = isMedia ? media : core;
    try {
      if (!(isMedia && await cache.match(url))) {
        const resp = await fetch(url, { cache: 'no-cache' });
        if (!resp.ok) throw new Error(resp.status);
        await cache.put(url, resp);
      }
    } catch (e) {
      failed++;
    }
    done++;
    await report();
  }
}
