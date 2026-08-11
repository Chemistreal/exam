/* ============================================================
   창구를 몇 번 두드리나 — 셀 수 있게 못 박는다
   ------------------------------------------------------------
   앱스크립트는 실행을 **한 줄로 세운다.** 다섯 개를 동시에 보내도 저쪽에서는
   차례로 하나씩 돈다 — 앞엣것이 끝나야 뒤엣것이 시작한다. 그래서 '몇 번
   부르나' 가 곧 '얼마나 기다리나' 다.

   실제 브라우저로 재어 보니 셸을 여는 것만으로 **DT 창구를 여덟 번** 불렀다.

       names · pending · absentees · passed · cohortmis   (다섯이 한꺼번에)
       sentlog → snoozelog → views                        (앞엣것이 와야 다음)

   뒤의 셋은 폭포였다. 창구 하나에 한 번씩 실행이 도니 한꺼번에 보내면 줄만
   길어진다고 보고 일부러 차례로 걸어 뒀는데, 묶음 창구가 생긴 지금은 반대다.

   고친 뒤: **두 번**(급한 것 한 묶음 · 꾸미는 것 한 묶음).

   여기서 지키는 것:
   - 첫 화면에서 DT 창구를 세 번 넘게 두드리지 않는다
   - 묶음이 실제로 묶여 나간다(want 에 이름이 여럿)
   - 묶음으로 받은 것이 낱개로 받은 것과 **같은 자리에 들어간다**
   - 묶음 창구가 없는 옛 배포에서도 화면이 산다 (하나씩 다시 묻는다)
   - 그때도 화면의 숫자는 같다 — 느려질 뿐 안 깨진다

   ⚠ 이 검사는 진짜 시트를 부르지 않는다. 앱스크립트로 가는 길을 전부
     가로채고 흉내 낸 답만 준다.

   실행:
       node tests/hub-batch.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
/* 포트를 그 자리에서 받고, 서버가 **대답할 때까지** 기다린다.
   고정 포트를 박아 두면 검사 두 벌이 겹칠 때 뒤엣것이 빈 화면을 보고
   "그게 화면에 없다" 고 말한다 — tests/_serve.js 머리말. */
const { serve } = require('./_serve.js');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
/* 번호를 안 박는다(0 이면 빈 포트를 받는다). `PORT` 를 준 자리는 그대로 쓴다.
   **서버를 띄운 뒤 실제로 받은 번호로 채운다** — 아래 `serve()` 바로 다음. */
let PORT = Number(process.env.PORT || 0);
const ROOT = path.join(__dirname, '..');
/* DT 창구의 배포 주소. KMChC 도 'names' 를 쓰므로 앱을 가려 세지 않으면
   이 검사가 무엇을 세는지 모르게 된다. */
const DT_EP = 'AKfycbzvFaPXgEgCBQ8HowtP8tPTtdiIVFtmZSUf0KFXUOVOh3ektrFMkz4KSR4I52LDBzB8rw';

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

/* 창구 하나가 주는 답. 묶음이든 낱개든 **같은 것**을 준다 — 그래야 둘을
   견줄 수 있다. 숫자는 화면에 그대로 뜨는 것들이라 자리를 확인할 수 있다. */
function partOf(action) {
  switch (action) {
    case 'names': return { ok: true, classes: [
      { label: '화학1 토1:30', course: 'ch1', students: [
        { name: '김지성', school: '휘문중', year: '2' },
        { name: '최예린', school: '역삼중', year: '2' } ] } ] };
    case 'pending': return { ok: true, pending: { activeDays: 14, generatedAt: 'T', stale: [], active: [
      { studentKey: 's1', name: '최예린', school: '역삼중', year: '2', course: 'ch1', round: 12,
        lastAttempt: '정시', nextNeeded: '재시', score: 68, days: 9, lastDate: '6/17',
        reportLink: 'https://x/report.html?student=a', active: true } ] } };
    case 'absentees': return { ok: true, absentees: { generatedAt: 'T', classes: [
      { label: '화학1 토1:30', course: 'ch1', round: 12, total: 8, present: 6,
        absent: ['김도윤', '김지성'] } ] } };
    case 'passed': return { ok: true, passed: { days: 14, generatedAt: 'T', passed: [] } };
    case 'cohortmis': return { ok: true, rows: [] };
    case 'sentlog': return { ok: true, sent: [] };
    case 'snoozelog': return { ok: true, snoozed: [] };
    case 'views': return { ok: true, views: [] };
    default: return { ok: true };
  }
}

/* 셸을 한 번 열고, DT 창구로 나간 것을 그대로 적는다.
   bundle 을 아는 창구(묶음 배포)와 모르는 창구(옛 배포) 둘 다 흉내 낸다. */
async function run(browser, knowsBundle) {
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 },
                                         serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.addInitScript(() => {
    try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
  });
  await p.route('**/DT/**', route => route.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8', body: '<!doctype html><meta charset="utf-8">' }));

  const hits = [];
  await p.route('**/macros/s/**', route => {
    const u = new URL(route.request().url());
    const cb = u.searchParams.get('callback') || 'cb';
    const act = u.searchParams.get('action') || '';
    const isDT = u.pathname.includes(DT_EP);
    if (isDT) hits.push({ action: act, want: u.searchParams.get('want') || '' });
    let body;
    if (isDT && act === 'bundle') {
      if (!knowsBundle) {
        /* 옛 배포는 bundle 을 모른다. action 이 안 걸리면 성적표 길로 가서
           엉뚱한 모양이 온다 — 셸은 그것을 '묶음 없음' 으로 보고 하나씩 다시
           물어야 한다. */
        body = { ok: true, student: null, rows: [] };
      } else {
        const parts = {};
        String(u.searchParams.get('want') || '').split(',')
          .filter(Boolean).forEach(a => { parts[a] = partOf(a); });
        body = { ok: true, bundle: true, parts: parts, n: Object.keys(parts).length };
      }
    } else if (isDT) {
      body = partOf(act);
    } else {
      body = { ok: true, students: [] };      // KMChC
    }
    return route.fulfill({ status: 200, contentType: 'text/javascript',
      body: cb + '(' + JSON.stringify(body) + ');' });
  });

  await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);
  /* 화면에 실제로 자리를 잡았는지 본다. 호출 수만 세면 '한 번 부르고 아무것도
     안 그리는' 것이 제일 좋은 점수를 받는다. */
  const seen = await p.evaluate(() => ({
    /* 반 명단이 들어왔나 (names) */
    roster: (window.dtCached ? (window.dtCached('names') || []).length : -1),
    /* 미응시가 들어왔나 (absentees) */
    abs: (typeof ABS_ROWS !== 'undefined' && ABS_ROWS) ? ABS_ROWS.length : -1,
    /* 재시 대기가 들어왔나 (pending). 셸은 이것을 **배열로 펴서** 담는다
       (DT 가 주는 {active, stale} 중 active 만 남긴다). */
    pend: (window.dtCached ? (window.dtCached('pending') || []).length : -1),
  })).catch(() => ({ roster: -1, abs: -1, pend: -1 }));
  await ctx.close();
  return { hits, errs, seen };
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(
    Object.assign({ args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));

  let neu, old;
  try {
    console.log('── 묶음 창구가 있는 배포 ──');
    neu = await run(browser, true);
    console.log('  DT 호출 ' + neu.hits.length + '회 · ' +
      JSON.stringify(neu.hits.map(h => h.action + (h.want ? '(' + h.want + ')' : ''))));
    chk('첫 화면에서 DT 창구를 세 번 넘게 두드리지 않는다', neu.hits.length <= 3, true);
    chk('묶음으로 나간다', neu.hits.every(h => h.action === 'bundle'), true);
    chk('한 묶음에 둘 이상을 담는다',
      neu.hits.some(h => h.want.split(',').filter(Boolean).length >= 2), true);
    chk('반 명단이 화면에 들어왔다', neu.seen.roster, 2);
    chk('미응시가 화면에 들어왔다', neu.seen.abs, 1);
    chk('재시 대기가 화면에 들어왔다', neu.seen.pend, 1);
    chk('콘솔에 예외가 없다', neu.errs, []);

    console.log('\n── 묶음 창구가 없는 옛 배포 ──');
    old = await run(browser, false);
    const solo = old.hits.filter(h => h.action !== 'bundle').map(h => h.action);
    console.log('  DT 호출 ' + old.hits.length + '회 · 낱개로 다시 물은 것 ' + JSON.stringify(solo));
    chk('묶음이 안 되면 하나씩 다시 묻는다', solo.length >= 2, true);
    chk('그래도 반 명단이 들어온다', old.seen.roster, 2);
    chk('그래도 미응시가 들어온다', old.seen.abs, 1);
    chk('그래도 재시 대기가 들어온다', old.seen.pend, 1);
    chk('콘솔에 예외가 없다', old.errs, []);

    console.log('\n── 두 길이 같은 것을 준다 ──');
    chk('묶음이든 낱개든 화면의 숫자가 같다', neu.seen, old.seen);
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
