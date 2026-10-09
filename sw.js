/**
 * Service Worker for JEE Advanced AIR-1 App
 * Enables offline access, resource caching, and standalone mobile PWA functionality.
 */

const CACHE_NAME = 'jee-air1-cache-v1';
const ASSETS_TO_CACHE = [
  '/nopeit-sn/',
  '/nopeit-sn/index.html',
  '/nopeit-sn/style.css',
  '/nopeit-sn/app.js',
  '/nopeit-sn/manifest.json',
  '/nopeit-sn/icon-192.png',
  '/nopeit-sn/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch(err => {
        console.warn('Some assets could not be cached immediately:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network first with cache fallback for dynamic API, cache-first for static assets
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ error: 'Offline mode: Network unavailable' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
  } else {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request);
      })
    );
  }
});
