// Service worker Coup d'Aile
// Cache le coeur vital pour un fonctionnement hors-ligne.
// REGLE : on ne met en cache QUE l'app-shell de notre propre origine.
// Toute requete vers un service tiers (Supabase, Wikipedia, Open-Meteo, Base Adresse
// Nationale, tuiles OpenStreetMap) part directement au reseau, sans jamais passer par
// le cache. Sinon les donnees du carnet resteraient figees apres un ajout, une
// modification ou une suppression.
const CACHE = 'coup-daile-v19';
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (_) { return; }

  // Tout ce qui n'est pas notre origine part au reseau, sans cache et sans interception.
  if (url.origin !== self.location.origin) return;

  // Navigation : reseau d'abord, repli sur le cache si hors-ligne.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put('./index.html', copy));
          return resp;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // App-shell (icones, manifest, ressources statiques) : cache d'abord.
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((resp) => {
          if (resp && resp.status === 200 && resp.type === 'basic') {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return resp;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});
