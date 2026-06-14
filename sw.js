/* Chemistreal 서비스워커
 * 전략: HTML/내비게이션은 network-first(항상 최신 배포 우선, 오프라인 시 캐시),
 *       아이콘/매니페스트 등 정적 자원은 cache-first.
 * 배포 갱신이 사용자에게 즉시 전파되도록 한다. 단일 파일 운영에도 안전.
 */
const VERSION = '2026.06.4';
const CACHE = 'chemistreal-' + VERSION;
const ASSETS = ['./', './index.html', './note.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isHTML(req) {
  if (req.mode === 'navigate') return true;
  const a = req.headers.get('accept') || '';
  return a.includes('text/html');
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // 시트/폰트 등 외부 요청은 그대로 통과

  if (isHTML(req)) {
    // network-first: 최신 index.html 우선, 실패하면 캐시
    e.respondWith(
      fetch(req).then(resp => {
        const cp = resp.clone();
        caches.open(CACHE).then(c => c.put(req, cp)).catch(() => {});
        return resp;
      }).catch(() => caches.match(req).then(r => r || caches.match('./index.html')))
    );
    return;
  }
  // cache-first: 정적 자원
  e.respondWith(
    caches.match(req).then(r => r || fetch(req).then(resp => {
      const cp = resp.clone();
      caches.open(CACHE).then(c => c.put(req, cp)).catch(() => {});
      return resp;
    }).catch(() => r))
  );
});

// 새 버전 활성화 신호를 페이지가 보내면 즉시 교체
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });
