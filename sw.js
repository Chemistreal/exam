/* Chemistreal 서비스워커
 *
 * 캐시를 둘로 나눈다.
 *
 *   shell — HTML·아이콘·매니페스트. 배포마다 새로 받아야 하므로 VERSION 을 달고,
 *           새 버전이 활성화되면 옛 shell 캐시는 통째로 지운다.
 *   data  — crops/·donghyung/·answers/. 문항 이미지는 한 번 만들면 바뀌지 않고,
 *           양이 크다(crops 만 51MB). 배포할 때마다 버리면 학생이 매번 다시
 *           받아야 하므로 버전을 달지 않고 남겨 둔다.
 *
 * 가져오는 방법도 셋으로 나눈다.
 *
 *   HTML          network-first — 배포 갱신이 즉시 전파되어야 한다
 *   crops/        cache-first   — 한 번 받으면 그만. 바뀌지 않는다
 *   donghyung/·answers/
 *                 stale-while-revalidate — 캐시를 먼저 주고 뒤에서 새로 받아
 *                 다음 번을 준비한다. 해설을 고치면 다음 열람부터 반영된다
 *
 * 그리고 페이지가 `{type:'warm', urls:[...]}` 를 보내면 그 목록을 미리 받아
 * data 캐시에 넣는다. 오답노트는 자기가 틀린 문항의 이미지만 필요하므로,
 * 화면에 뜬 뒤 곧바로 미리 받아 두면 학생이 나중에 오프라인이 되어도 열린다.
 * (`loading="lazy"` 라 스크롤하지 않은 이미지는 저절로는 캐시되지 않는다)
 */
const VERSION = 'cb98413daf20';
const SHELL = 'chemistreal-shell-' + VERSION;
const DATA = 'chemistreal-data';          // 버전 없음 — 배포해도 남긴다
const ASSETS = ['./', './index.html', './note.html', './hub.html', './final.html', './final-submit.html',
                './exams.json', './cohort/baseline.json',
                './manifest.json', './icon-192.png', './icon-512.png'];

// data 캐시에 넣을 경로. 여기 없는 것은 shell 로 간다.
const IMMUTABLE = /\/crops\//;                       // 바뀌지 않는다
const REFRESHABLE = /\/(donghyung|answers)\/|exams\.json$/;   // 고칠 수 있다

/* ⚠ `cohort/` 를 여기서 **빼냈다**(2026-08-10).
 *
 * 선생님 말씀 — "2017인데도 총인원이 11명으로 표시되니까 데이터가 빠진거지".
 * 저장소에는 hwol-2017 이 100명으로 들어 있고, 손에서 재면 111명(기준 100 +
 * 이번 11)이 제대로 나온다. **파일에는 있는데 그 기기까지 안 간 것이다.**
 *
 * 까닭이 이 줄이었다. `cohort/` 가 REFRESHABLE 이면 stale-while-revalidate 라
 * **캐시를 먼저 주고** 새것은 *다음* 열람용으로만 받아 둔다. 게다가 그 캐시는
 * `chemistreal-data` — **버전이 없어서 배포해도 안 지워진다.** 그래서 기준
 * 기록이 열두 회차 늘어난 뒤에도 옛 파일이 그 기기에 그대로 앉아 있었다.
 *
 * 해설(donghyung·answers)은 하루 늦게 반영돼도 된다. **석차의 분모는 아니다** —
 * 학부모가 받는 종이에 찍히는 숫자이고, 낡으면 "10/11" 처럼 **틀린 것처럼
 * 보이지 않으면서 틀린다.** 그래서 HTML 과 같은 칸으로 옮긴다: 망을 먼저 보고
 * 안 되면 그때만 캐시. 45KB 라 값도 싸다.
 *
 * (2026-08-03 에 옛 final.html 이 캐시에서 나오던 일과 같은 갈래다. 그때는
 *  VERSION 을 내용에서 짓게 해 막았는데, data 캐시는 그 VERSION 을 안 탄다.) */
const FRESH = /\/cohort\//;

self.addEventListener('install', e => {
  // addAll 은 하나라도 404 면 전부 실패한다. 파일 목록이 바뀌어도 설치가
  // 깨지지 않도록 하나씩 넣는다.
  e.waitUntil(caches.open(SHELL).then(c =>
    Promise.all(ASSETS.map(u => c.add(u).catch(() => {})))
  ));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(
        // 옛 shell 만 지운다. data 는 남긴다(crops 51MB 를 매 배포마다 다시
        // 받게 할 수는 없다).
        ks.filter(k => k.startsWith('chemistreal-shell-') && k !== SHELL).map(k => caches.delete(k))
      ))
      /* ⚠ 다만 `cohort/` 만은 data 에서 **뽑아낸다.** 예전에는 이것도 data 로
         갔는데, data 는 버전이 없어 배포해도 안 지워진다. 그래서 기준 기록이
         늘어난 뒤에도 옛 사본이 기기에 앉아 "총인원 11명" 같은 숫자를 만들었다.
         이제는 망에서 받지만, **이미 앉아 있는 옛 사본**은 여기서 치운다.
         한 번만 돌면 되고, 남겨 두면 다음 사람이 이 자리를 또 의심한다. */
      .then(() => caches.open(DATA).then(c => c.keys().then(rs => Promise.all(
        rs.filter(r => FRESH.test(new URL(r.url).pathname)).map(r => c.delete(r))
      ))).catch(() => {}))
      .then(() => self.clients.claim())
  );
});

function isHTML(req) {
  if (req.mode === 'navigate') return true;
  return (req.headers.get('accept') || '').includes('text/html');
}

/* 캐시에 넣을 때는 URL 문자열을 열쇠로 쓴다.
   페이지가 `fetch(u,{cache:'no-store'})` 로 부르는 곳이 있어서 Request 를 그대로
   열쇠로 넘기면 브라우저에 따라 거부당한다. URL 로 넣으면 그 문제가 없다. */
function put(cacheName, url, resp) {
  if (!resp || !resp.ok || resp.type === 'opaque') return;
  const copy = resp.clone();
  caches.open(cacheName).then(c => c.put(url, copy)).catch(() => {});
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;   // 시트·폰트 등 외부 요청은 그대로 통과
  const key = url.pathname + url.search;

  if (isHTML(req)) {
    e.respondWith(
      fetch(req)
        .then(resp => { put(SHELL, key, resp); return resp; })
        .catch(() => caches.match(key).then(r => r || caches.match('./index.html')))
    );
    return;
  }

  /* 석차의 분모. 낡은 값은 **틀린 것처럼 보이지 않으면서 틀린다** — 위 FRESH
     주석 참고. 망을 먼저 보고, 못 닿을 때만 캐시를 준다(오프라인에서도 화면이
     빈칸이 되지는 않는다). 옛 shell 과 함께 지워지도록 SHELL 에 넣는다. */
  if (FRESH.test(url.pathname)) {
    e.respondWith(
      fetch(req)
        .then(resp => { put(SHELL, key, resp); return resp; })
        .catch(() => caches.match(key))
    );
    return;
  }

  if (IMMUTABLE.test(url.pathname)) {
    e.respondWith(
      caches.match(key).then(hit => hit || fetch(req).then(resp => { put(DATA, key, resp); return resp; }))
    );
    return;
  }

  if (REFRESHABLE.test(url.pathname)) {
    // 캐시를 먼저 주고, 뒤에서 새로 받아 다음 열람을 준비한다.
    // 캐시가 있으면 `live` 는 아무도 기다리지 않는 약속이 되므로 catch 를 반드시
    // 붙인다. 오프라인에서 이게 거부되면 처리되지 않은 거부로 콘솔에 찍힌다.
    e.respondWith(
      caches.match(key).then(hit => {
        const live = fetch(req)
          .then(resp => { put(DATA, key, resp); return resp; })
          .catch(err => { if (hit) return hit; throw err; });
        return hit || live;
      })
    );
    return;
  }

  e.respondWith(
    caches.match(key).then(hit => hit || fetch(req)
      .then(resp => { put(SHELL, key, resp); return resp; })
      .catch(() => hit))
  );
});

self.addEventListener('message', e => {
  const msg = e.data;
  if (msg === 'skipWaiting') { self.skipWaiting(); return; }
  if (!msg || msg.type !== 'warm' || !Array.isArray(msg.urls)) return;

  // 이미 있는 것은 건너뛰고 없는 것만 받는다. 실패해도 조용히 넘어간다 —
  // 미리 받기는 되면 좋은 것이지, 되지 않는다고 화면이 잘못되지는 않는다.
  e.waitUntil(caches.open(DATA).then(async cache => {
    let added = 0;
    for (const raw of msg.urls.slice(0, 400)) {
      const key = new URL(raw, location.href).pathname;
      try {
        if (await cache.match(key)) continue;
        const resp = await fetch(key, { credentials: 'same-origin' });
        if (resp.ok) { await cache.put(key, resp); added++; }
      } catch (err) { /* 오프라인이거나 없는 파일 — 넘어간다 */ }
    }
    const clients = await self.clients.matchAll();
    clients.forEach(c => c.postMessage({ type: 'warmed', added: added, asked: msg.urls.length }));
  }));
});
