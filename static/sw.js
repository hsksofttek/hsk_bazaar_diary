const CACHE_VERSION = 'v3';
const STATIC_CACHE = `biz-static-${CACHE_VERSION}`;
const OFFLINE_URL = '/static/offline.html';
const ASSETS = [
  '/static/offline.html',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/css/responsive.css',
  '/static/js/ui.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== STATIC_CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Bypass non-GET (avoid caching POST/PUT/DELETE/etc.)
  if (req.method !== 'GET') return;

  // Never cache API calls
  if (url.pathname.startsWith('/api/')) return;

  // Navigation requests: network-first, fallback to offline
  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(req).then(res => res).catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Cache-first for static assets (CSS/JS/images/icons) with defensive checks
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(res => {
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(STATIC_CACHE).then(cache => cache.put(req, copy));
        }
        return res;
      }).catch(() => cached)
    })
  );
});
