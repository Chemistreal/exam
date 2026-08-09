/* ============================================================
   허브가 창구를 **몇 번** 두드리는가
   ------------------------------------------------------------
   앱스크립트는 실행을 **한 줄로 세운다.** 그래서 창구 호출 수는 곧 기다리는
   시간이고, 더 나쁘게는 **다른 화면의 실패**다 — 셸이 여덟 번을 한꺼번에
   두드리는 동안 명단 화면(roster.html)이 자기 요청을 줄에서 놓치고 기본
   명단으로 되돌아가 "저장하면 반영됩니다" 배너를 띄운 적이 있다. 시트도
   명단도 멀쩡했는데 하마터면 덮어쓸 뻔했다.

   그래서 열 번을 네 번으로 줄여 두었다(`bundle` 로 다섯 갈래를 한 번에).
   줄여 놓은 것은 **말없이 되돌아간다** — 창구를 하나 더 부르는 줄은 한 줄이고,
   화면은 멀쩡해 보이고, 아무 검사도 안 걸린다. 숫자로 박아 둔다.

   잰 값 (2026-08-09 · 실제 브라우저):

       첫 화면      4번   names · bundle[5갈래] · bundle[3갈래] · all
       학생 탭      +0     반 탭 +0     회차 탭 +0
       개념 탭      +1     자료 탭 +0
       같은 탭에 두 번째로 들어가면  +0  (DT_CACHE)

   ⚠ 이 값을 **한 번 잘못 쟀다.** 처음에는 개념 탭 +5, 자료 탭 +2 로 나왔는데,
     그때는 창구가 **닿지 않는 상태**로 재고 있었다. 실패한 응답은 캐시에 안
     앉으므로 다시 그릴 때마다 또 부른다 — 즉 그 숫자는 '평소' 가 아니라
     '고장 났을 때' 였다. 선생님이 실제로 겪는 값은 위와 같다.
     **대답이 오는 상태로 재야 한다.**

   ⚠ 잠금은 **화면이 뜨기 전에** 심는다. 예전에 이 값을 두 번 잘못 쟀는데,
     잠금을 풀려고 `goto` 뒤에 `reload` 를 해서 화면이 두 번 떴기 때문이다 —
     창구 수가 그대로 두 배로 나왔다.
   ⚠ 늘어나면 빨간불, 줄어들면 통과다. 자물쇠는 **되돌아가는 것**만 막는다.

   실행:
       node tests/hub-calls.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const { spawn } = require('child_process');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8940);
const ROOT = path.join(__dirname, '..');

/* 되돌아가면 안 되는 값. 줄이면 여기 숫자도 같이 내린다. */
const LOCK = { boot: 4, stu: 0, cls: 0, rnd: 0, con: 1, mat: 0 };

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

(async () => {
  const srv = spawn(process.execPath, ['-e', `
    const http=require('http'),fs=require('fs'),p=require('path');
    const T={'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.css':'text/css'};
    http.createServer((q,s)=>{
      const f=p.join(${JSON.stringify(ROOT)}, decodeURIComponent(q.url.split('?')[0]));
      fs.readFile(f,(e,d)=>e?(s.writeHead(404),s.end()):(s.writeHead(200,{'Content-Type':T[p.extname(f)]||'text/plain'}),s.end(d)));
    }).listen(${PORT});
  `], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 700));

  const browser = seal(await chromium.launch(
    Object.assign({ args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));

  const calls = [];
  p.on('request', r => {
    const u = r.url();
    if (u.includes('script.google.com')) {
      try {
        const q = new URL(u).searchParams;
        calls.push((q.get('action') || '?') +
          (q.get('want') ? '[' + q.get('want').split(',').length + '갈래]' : ''));
      } catch (e) { calls.push('?'); }
    }
  });

  /* 잠금은 화면이 뜨기 **전에** 심는다 — reload 로 풀면 화면이 두 번 뜬다. */
  await p.addInitScript(() => {
    try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
  });
  await p.route('**/DT/**', r => r.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8">' }));
  /* 대답은 바로 준다. 늦게 주면 탭을 옮길 때 아직 안 온 것과 섞인다. */
  await p.route('**/macros/s/**', r => {
    const u = new URL(r.request().url()), cb = u.searchParams.get('callback') || 'cb';
    const a = u.searchParams.get('action');
    const one = () => ({ ok: true, classes: [], students: [], rows: [],
      pending: { active: [] }, passed: { passed: [] }, absentees: { classes: [] },
      mis: { rows: [] }, sent: [], snoozed: [], views: [], history: [] });
    let body;
    if (a === 'bundle') {
      const ps = {};
      String(u.searchParams.get('want') || '').split(',').filter(Boolean)
        .forEach(x => { ps[x] = one(); });
      body = { ok: true, bundle: true, parts: ps };
    } else body = one();
    return r.fulfill({ status: 200, contentType: 'text/javascript',
      body: cb + '(' + JSON.stringify(body) + ');' });
  });

  try {
    await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p.waitForFunction(() => typeof show === 'function', null, { timeout: 20000 });
    await p.waitForTimeout(5000);
    const boot = calls.slice();
    console.log('  첫 화면 ' + boot.length + '번: ' + boot.join(' · '));
    chk('첫 화면에서 창구를 부르는 횟수', boot.length, LOCK.boot);

    /* ⚠ 탭마다 **한 번씩만** 재고 끝내면 안 된다. 두 번째로 들어갔을 때도
       또 부르면 캐시가 안 듣는 것인데, 한 번만 재면 그것을 못 본다. */
    const per = {};
    for (const t of ['stu', 'cls', 'rnd', 'con', 'mat']) {
      const n0 = calls.length;
      await p.evaluate(id => show(id), t);
      await p.waitForTimeout(1800);
      per[t] = calls.length - n0;
    }
    console.log('  탭마다 더 부른 횟수: ' +
      Object.entries(per).map(([k, v]) => k + ' +' + v).join(' · '));
    ['stu', 'cls', 'rnd', 'con', 'mat'].forEach(t => {
      chk(`${t} 탭이 더 부르는 횟수`, per[t], LOCK[t]);
    });

    /* 같은 탭에 두 번째로 들어가면 하나도 안 불러야 한다(DT_CACHE). */
    const again = {};
    for (const t of ['stu', 'cls', 'rnd', 'con', 'mat']) {
      const n0 = calls.length;
      await p.evaluate(id => show('dash'), t);
      await p.waitForTimeout(200);
      await p.evaluate(id => show(id), t);
      await p.waitForTimeout(1200);
      again[t] = calls.length - n0;
    }
    console.log('  두 번째로 들어갔을 때: ' +
      Object.entries(again).map(([k, v]) => k + ' +' + v).join(' · '));
    chk('두 번째로 들어가면 아무것도 다시 안 부른다',
        Object.values(again).reduce((a, b) => a + b, 0), 0);

    chk('콘솔에 예외가 없다', errs, []);
  } finally {
    await browser.close();
    srv.kill();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
