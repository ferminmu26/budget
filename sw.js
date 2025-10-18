const CACHE_NAME = 'finanza-mia-cache-v2'; // Incrementamos la versión del caché
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo.png',
  '/screenshot1.png', // <-- Archivo nuevo
  '/screenshot2.png'  // <-- Archivo nuevo
];

// Evento de instalación: guarda los archivos en la caché
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache and caching files');
        return cache.addAll(urlsToCache);
      })
  );
});

// Evento activate: limpia las cachés viejas
self.addEventListener('activate', event => {
  console.log('Service worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service worker: clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Evento fetch: sirve los archivos desde la caché si es posible
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Si el archivo está en la caché, lo devuelve. Si no, lo busca en la red.
        return response || fetch(event.request);
      })
  );
});

