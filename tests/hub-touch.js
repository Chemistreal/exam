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
const noSheet = require('./_nosheet.js');
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
        students: [S('박바다', '대청중', '3')] } ] },
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
      /* [바뀐 것] 2026-08-15 — 숫자 칸이 흰 상자(.card) 에서 「오늘 머리판」
         안의 .hn 으로 바뀌었다. 지키려던 것은 «급한 것이 앞에 온다» 이지
         상자 이름이 아니므로 새 자리를 본다. */
      카드순서: [...document.querySelectorAll('#dashCards .hn')]
        .map(c => { const b = c.querySelector('.hn__v'); return b ? b.id : ''; })
        .filter(Boolean),
      급한카드Y: ab ? Math.round(ab.getBoundingClientRect().top + scrollY) : null,
      /* 머리가 세로를 얼마나 먹는가. 폰을 눕히면 이 값이 51% 까지 갔다. */
      머리: Math.round((document.querySelector('header') || { getBoundingClientRect: () => ({ height: 0 }) })
        .getBoundingClientRect().height),
    };
  }, TAP_MIN);

  /* ⚠ 줄이 터지는 것은 **반 탭**에서 본다. 대시보드에 있는 채로 재면 그 줄들이
     아직 안 그려져 있어 늘 '없음' 이 나온다 — 검사가 조용히 아무것도 안 보게
     된다. 대시보드 것을 먼저 재고 나서 탭을 옮긴다. */
  /* ⚠ 대시보드도 같이 본다. 처음에는 반 탭만 재고 넘어갔는데, 대시보드의
     '반별 인원' 줄에서 과목 칸('화학Ⅰ')이 폭 13px 로 짜부러져 세로로 쪼개져
     있었다 — 한 탭만 재면 나머지는 안 재는 것과 같다. */
  const look1 = () => p.evaluate(() => ({
    쪼개진칸: [...document.querySelectorAll('.list .row span, .mult .row span')]
      .filter(e => {
        if (e.children.length) return false;
        const t = (e.textContent || '').trim();
        if (t.length < 2) return false;
        const b = e.getBoundingClientRect();
        if (!b.width || !b.height) return false;
        const lh = parseFloat(getComputedStyle(e).lineHeight) || 18;
        return Math.round(b.height / lh) >= 3 && b.width < 40;
      })
      .map(e => (e.textContent || '').trim().slice(0, 10) + ' ' +
                Math.round(e.getBoundingClientRect().width) + 'px'),
    칸밖단추: [...document.querySelectorAll('button')]
      .filter(e => {
        const b = e.getBoundingClientRect();
        if (!b.width || e.closest('nav')) return false;
        const box = e.closest('section, .list, .note, .card');
        return box && b.right > box.getBoundingClientRect().right + 1;
      })
      .map(e => (e.textContent || '').trim().slice(0, 10)),
  }));
  const dash = await look1();

  await p.evaluate(() => { if (window.show) show('cls'); });
  await p.waitForTimeout(900);
  const rows = await p.evaluate(() => ({
    쪼개진칸: [...document.querySelectorAll('.list .row span')]
      .filter(e => {
        if (e.children.length) return false;
        const t = (e.textContent || '').trim();
        if (t.length < 2) return false;
        const b = e.getBoundingClientRect();
        if (!b.width || !b.height) return false;
        const lh = parseFloat(getComputedStyle(e).lineHeight) || 18;
        return Math.round(b.height / lh) >= 3 && b.width < 40;
      })
      .map(e => (e.textContent || '').trim().slice(0, 10) + ' ' +
                Math.round(e.getBoundingClientRect().width) + 'px'),
    칸밖단추: [...document.querySelectorAll('button')]
      .filter(e => {
        const b = e.getBoundingClientRect();
        if (!b.width || e.closest('nav')) return false;
        const box = e.closest('section, .list, .note, .card');
        return box && b.right > box.getBoundingClientRect().right + 1;
      })
      .map(e => (e.textContent || '').trim().slice(0, 10)),
    반줄수: document.querySelectorAll('#clsList .row').length,
  }));
  await ctx.close();
  /* 대시보드에서 본 것과 반 탭에서 본 것을 합쳐서 돌려준다. */
  rows.쪼개진칸 = dash.쪼개진칸.concat(rows.쪼개진칸);
  rows.칸밖단추 = dash.칸밖단추.concat(rows.칸밖단추);
  return Object.assign(m, rows, { errs: errs });
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(
    Object.assign({ args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(browser);

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

    console.log('  반 탭 줄 ' + 폰.반줄수 + '개 · 쪼개진 칸: ' +
                (폰.쪼개진칸.length ? JSON.stringify(폰.쪼개진칸) : '없음') +
                ' · 칸 밖 단추: ' + (폰.칸밖단추.length ? JSON.stringify(폰.칸밖단추) : '없음'));
    /* 줄이 아예 안 그려졌으면 위 둘은 늘 '없음' 이다 — 안 재고 통과하는 것을 막는다. */
    chk('반 탭에 줄이 실제로 그려졌다', 폰.반줄수 > 0, true);
    chk('글자가 한 글자씩 세로로 쪼개지지 않는다', 폰.쪼개진칸, []);
    chk('단추가 칸 밖으로 안 나간다', 폰.칸밖단추, []);

    /* ── 폰을 가로로 눕혔을 때 ────────────────────────────────────────
       좁은 화면 규칙은 **폭**으로 가른다(560px). 그런데 폰을 눕히면 폭이
       844px 이 되어 그 규칙이 통째로 풀린다 — 재어 보니 머리가 197px,
       **화면의 51%** 였다(세로일 때는 120px·14%). 반이 머리인 화면에서는
       숫자 하나 보려고 스크롤해야 한다. 높이로도 가르게 고쳤다. */
    console.log('\n── 폰을 눕혔을 때 844×390 ──');
    const 가로 = await look(browser, { width: 844, height: 390, touch: true });
    console.log(`  머리 ${가로.머리}px (화면의 ${Math.round(가로.머리 / 390 * 100)}%)`);
    chk('눕혀도 머리가 화면의 3분의 1을 안 넘는다', 가로.머리 <= 130, true);
    chk('눕혀도 가로 스크롤이 안 생긴다', 가로.가로스크롤, false);
    chk('눕혀도 급한 것이 앞이다', 가로.카드순서.slice(0, 3), ['abCnt', 'pdCnt', 'dtCnt']);
    chk('눕혀도 콘솔에 예외가 없다', 가로.errs, []);

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
    chk('넓은 화면에서도 칸 밖으로 안 나간다', 노트북.칸밖단추, []);
    chk('가로 스크롤이 안 생긴다', 노트북.가로스크롤, false);
    chk('콘솔에 예외가 없다', 노트북.errs, []);
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
