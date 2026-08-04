/* ============================================================
   손가락으로 쓰는 기기에서 허브가 눌리는가
   ------------------------------------------------------------
   선생님은 수업 사이에 **휴대폰으로** 허브를 연다. 재어 보니 휴대폰
   (390×844)에서 이랬다.

       누르는 자리가 28px 인 것        25개
       키보드 단축키 안내가 먹는 높이   110px  (첫 화면의 13%)

   28px 은 손가락 끝(대략 7~9mm)보다 작다. '문자 복사'·'무시' 처럼 채점하는
   날 제일 많이 누르는 것들이 그 크기였다 — 보낸 표시를 무르려다 옆 학생
   문자를 복사하게 된다.

   키보드 안내는 더 나쁘다. 휴대폰에는 **키보드가 없다.** 눌러 볼 수 없는
   설명이 첫 화면의 110px 을 먹고, 그만큼 급한 숫자가 아래로 밀린다.

   고친 뒤: 작은 단추 **0개**, 안내문 **44px**.

   여기서 지키는 것:
   - 손가락 기기에서 누르는 자리가 32px 아래로 안 내려간다
   - 손가락 기기에서 키보드 안내가 안 보인다
   - **마우스 기기에서는 하나도 안 바뀐다** (거기서는 28px 로 충분하고,
     키우면 한 화면에 들어가던 목록이 밀려난다)
   - 가로 스크롤이 안 생긴다

   ⚠ 화면 폭으로 가르지 않는다. 폭이 좁아도 마우스를 쓰는 창이 있고, 넓어도
     손가락으로 쓰는 태블릿이 있다. **가리키는 장치**(pointer)로 가른다.
   ⚠ 탭 줄은 일부러 가로로 민다(.scr-r). 그 안의 단추가 화면 밖에 있는 것은
     넘친 것이 아니다 — 문서 폭이 화면 폭보다 큰지로 본다.

   실행:
       node tests/hub-touch.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const { spawn } = require('child_process');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8936);
const ROOT = path.join(__dirname, '..');
const DT_EP = 'AKfycbzvFaPXgEgCBQ8HowtP8tPTtdiIVFtmZSUf0KFXUOVOh3ektrFMkz4KSR4I52LDBzB8rw';
/* 손가락으로 누르는 자리의 최소 크기. 44px 이 흔히 쓰는 권고지만, 이 화면은
   목록이 촘촘한 것이 장점이라 36px 로 잡고 32px 아래로는 안 내려가게 지킨다. */
const TAP_MIN = 32;

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

/* 채점하는 날에 실제로 뜨는 만큼은 있어야 단추가 그려진다. */
function part(a) {
  const S = (n, sc, y) => ({ name: n, school: sc, year: y });
  const map = {
    names: { ok: true, classes: [
      { label: '화학1 일6-10', course: 'ch1', kind: 'dt',
        students: [S('강신우', '대치중', '2'), S('고영훈', '대신중', '1')] },
      { label: '파이널 목7-10', course: '', kind: 'exam',
        students: [S('박하람', '대청중', '3')] } ] },
    pending: { ok: true, pending: { active: [
      { name: '강신우', course: 'ch1', round: 12, lastAttempt: '정시',
        nextNeeded: '재시', score: 62, days: 5, studentKey: 's1' } ] } },
    passed: { ok: true, passed: { passed: [
      { name: '고영훈', course: 'ch1', round: 12, attempt: '정시',
        tries: 1, score: 96, date: '8/1', days: 2 } ] } },
    absentees: { ok: true, absentees: { classes: [
      { label: '화학1 일6-10', course: 'ch1', round: 12, total: 2, present: 1,
        absent: ['고영훈'] } ] } },
    cohortmis: { ok: true, rows: [] },
    sentlog: { ok: true, sent: [] }, snoozelog: { ok: true, snoozed: [] },
    views: { ok: true, views: [] }, mistags: { ok: true, mis: { rows: [] } },
  };
  return map[a] || { ok: true };
}

async function look(browser, { width, height, touch }) {
  const ctx = await browser.newContext({
    viewport: { width, height }, serviceWorkers: 'block',
    hasTouch: touch, isMobile: touch });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.addInitScript(() => {
    try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
  });
  await p.route('**/DT/**', r => r.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8">' }));
  await p.route('**/macros/s/**', r => {
    const u = new URL(r.request().url()), cb = u.searchParams.get('callback') || 'cb';
    const isDT = u.pathname.includes(DT_EP), a = u.searchParams.get('action');
    let body;
    if (isDT && a === 'bundle') {
      const ps = {};
      String(u.searchParams.get('want') || '').split(',').filter(Boolean)
        .forEach(x => { ps[x] = part(x); });
      body = { ok: true, bundle: true, parts: ps };
    } else if (isDT) body = part(a);
    else body = { ok: true, students: [] };
    return r.fulfill({ status: 200, contentType: 'text/javascript',
      body: cb + '(' + JSON.stringify(body) + ');' });
  });
  await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2600);
  const m = await p.evaluate(min => {
    const de = document.documentElement;
    const small = [...document.querySelectorAll('button, a[href], [role=button]')]
      .filter(e => {
        const r = e.getBoundingClientRect();
        if (!r.width || !r.height) return false;          // 안 보이는 것은 안 센다
        return r.height < min;
      })
      .map(e => (e.textContent || '').trim().slice(0, 12) + ' ' +
                Math.round(e.getBoundingClientRect().height) + 'px');
    const kb = document.querySelector('.kbdhint');
    const ab = document.querySelector('#abCnt');
    return {
      작은단추: small.length, 작은단추예: small.slice(0, 4),
      키보드안내보임: !!(kb && kb.getBoundingClientRect().height > 0),
      가로스크롤: de.scrollWidth > de.clientWidth,
      /* 숫자 칸이 놓인 차례. 급한 것이 앞에 와야 한다. */
      카드순서: [...document.querySelectorAll('#dashCards .card')]
        .map(c => { const b = c.querySelector('b'); return b ? b.id : ''; })
        .filter(Boolean),
      급한카드Y: ab ? Math.round(ab.getBoundingClientRect().top + scrollY) : null,
    };
  }, TAP_MIN);
  await ctx.close();
  return Object.assign(m, { errs: errs });
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

  try {
    console.log('── 휴대폰 (손가락) 390×844 ──');
    const 폰 = await look(browser, { width: 390, height: 844, touch: true });
    console.log(`  ${TAP_MIN}px 아래 단추 ${폰.작은단추}개 ${JSON.stringify(폰.작은단추예)}`);
    chk('누르는 자리가 손가락에 맞는다', 폰.작은단추, 0);
    chk('키보드 안내를 안 띄운다', 폰.키보드안내보임, false);
    chk('가로 스크롤이 안 생긴다', 폰.가로스크롤, false);
    chk('콘솔에 예외가 없다', 폰.errs, []);

    /* ── 급한 것이 앞에 온다 ──────────────────────────────────────────
       이 두 칸에는 원래부터 '채점하는 날 제일 급한 숫자' 라고 적혀 있었는데
       여덟 칸 중 일곱째·여덟째에 있었다. 휴대폰에서는 숫자 칸이 넉 줄이라
       급한 두 칸이 **맨 아랫줄**이었다 — 지난 것(오늘 채점·누적 학생)이 먼저
       보이고 지금 해야 할 일이 뒤에 있었다. */
    console.log('  카드 차례: ' + 폰.카드순서.join(' · '));
    chk('급한 두 칸이 맨 앞이다', 폰.카드순서.slice(0, 3), ['abCnt', 'pdCnt', 'dtCnt']);
    console.log(`  '시험 미응시' 카드 y=${폰.급한카드Y} (고치기 전 534)`);
    chk('첫 줄로 올라왔다', 폰.급한카드Y < 400, true);

    console.log('\n── 노트북 (마우스) 1280×900 ──');
    const 노트북 = await look(browser, { width: 1280, height: 900, touch: false });
    console.log(`  ${TAP_MIN}px 아래 단추 ${노트북.작은단추}개`);
    /* 마우스에서는 원래대로다. 여기까지 키우면 한 화면에 들어가던 목록이
       밀려난다 — 고치는 것이 아니라 망치는 것이다. */
    chk('마우스 화면은 촘촘한 채로 둔다', 노트북.작은단추 > 0, true);
    chk('키보드 안내는 그대로 보인다', 노트북.키보드안내보임, true);
    /* 순서는 화면 크기와 상관없이 같다 — 기기마다 다르면 손이 헷갈린다. */
    chk('마우스 화면에서도 급한 것이 앞이다',
        노트북.카드순서.slice(0, 3), ['abCnt', 'pdCnt', 'dtCnt']);
    chk('가로 스크롤이 안 생긴다', 노트북.가로스크롤, false);
    chk('콘솔에 예외가 없다', 노트북.errs, []);
  } finally {
    await browser.close();
    srv.kill();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
