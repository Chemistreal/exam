/* ============================================================
   **학생이 오답을 밟아 나가는 길** (브라우저 필요)
   ------------------------------------------------------------
   2026-08-11, 선생님 결정 #18 · #19 · #20 · #23 · #27.

   이 다섯은 «틀렸다» 를 «오늘 이걸 하면 된다» 로 바꾸는 자리들이다.
   숫자를 바꾸는 고침이 아니라서, 되돌아가도 아무 검사가 안 울린다.
   그래서 여기 박는다.

       #18  0 뒤에 또 0 이 오지 않게 — 한 문항만 세운다
       #19  서른 장을 사흘로 나눈다 (여덟 아래면 안 나눈다)
       #20  문항마다 «다시 풀었음» 을 스스로 센다
       #23  목차로 갈 때 «어느 영역부터» 를 들고 간다
       #27  분포를 몰라도 **난이도만은** 보인다

   ⚠ 이 검사는 **글의 좋고 나쁨을 안 본다.** 그 자리가 있는지, 그리고
     **지어내지 않는지**만 본다 — 근거 없는 최상급, 빈 막대, 시트로 새는 표시.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/student-path.js
   ============================================================ */
'use strict';
const path = require('path');
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH;
const ROOT = path.join(__dirname, '..');
let PORT = Number(process.env.PORT || 0);

let fail = 0;
const chk = (n, ok, extra) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (extra ? '  ' + extra : ''));
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

const EXAM = 'hwol-2018';   // 전국 공식 정답률(rate)이 실려 있는 회차

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  /* ⚠ 시트 창구는 **끊지 않는다 — 빈 답을 준다.** 처음에 이 자리를
       `ctx.route('**://script.google.com/**', r => r.abort())` 로 손수 막았다.
       내 컴퓨터에서는 열다섯 개가 다 초록불이었는데 CI 에서는 오답노트가
       한 장도 안 그려졌다(2026-08-11, 60초 뒤 끊김).

       `tests/_nosheet.js` 머리말에 이미 적혀 있던 말이다 —
       *"창구는 막지 않고 빈 답을 준다. 앱스크립트는 CORS 가 없어 JSONP 로
       부르는데, **그냥 끊으면 앱이 '맞추는 중' 에서 안 넘어가는 자리가 있다**"*.
       그리고 그 자는 주소의 `macros/s` 자리로 막는다 — 내가 쓴
       `script.google.com` 은 302 로 넘어가는 `script.googleusercontent.com`
       을 못 덮는다.

       이미 있는 자를 안 쓰고 손으로 다시 만들면, 그 자가 값 주고 배운 것도
       같이 안 쓰는 것이 된다. */
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 90)));

  /* 오답노트를 그리는 `hydrateWrongbook` 은 **async** 다. 그 안에서 무엇이
     던지면 화면에는 아무 일도 안 일어나고 `pageerror` 도 안 뜬다 — 삼켜진
     약속이 되어 `unhandledrejection` 으로만 남는다. 그것도 같이 줍는다.
     (2026-08-11: CI 에서 카드가 안 그려졌는데 자가 «60초 지났다» 밖에 못
      말했다. **왜** 안 그려졌는지는 여기서 줍는 것들이 말해 준다) */
  await p.addInitScript(() => {
    window.__rej = [];
    addEventListener('unhandledrejection', e =>
      window.__rej.push(String((e.reason && e.reason.stack) || e.reason).slice(0, 300)));
  });
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
    null, { timeout: 30000 });

  /* 스물두 개만 맞힌 학생 — 오답이 서른여섯이라 사흘로 갈린다. */
  await p.evaluate((id) => {
    localStorage.clear();
    const ex = FINAL_EXAMS.find(e => e.id === id);
    openExam(id);
    document.getElementById('nm').value = '홍길동';
    let ok = 0;
    for (let q = 1; q <= ex.nQ; q++) {
      if (ok < 22) { setAns(q, ex.key[q - 1]); ok++; }
      else setAns(q, (ex.key[q - 1] % 4) + 1);
    }
    scoreAuto();
  }, EXAM);
  /* ⚠ 카드가 **한 장 뜬 순간**에 읽으면 안 된다. 시트가 빈 답을 주고 나면
       앱은 성적표를 한 번 더 그린다(loadHist → rerenderReport). 그 틈에는
       오답노트가 잠깐 비어 있다. 실제로 그 틈에서 읽고 «사흘로 안 나뉜다 ·
       다시 풀었음이 0개다» 라고 말했다 — 화면은 멀쩡했고, 자가 지나가는
       순간을 본 것이다. **더 안 바뀔 때까지** 기다린다(초를 세지 않는다).

     ⚠ 여기서 끊기면 자는 «60초 지났다» 만 남긴다. 그것은 고장난 곳을 안
       짚는 말이라, 못 그렸으면 화면이 어디까지 갔는지를 적고 죽는다. */
  const drawn = await p.waitForFunction(() => {
    const root = document.getElementById('wrongbook');
    if (!root || !document.querySelectorAll('.wb-card').length) return false;
    const n = root.innerHTML.length;
    const w = (window.__wbStable = window.__wbStable || { n: -1, k: 0 });
    if (w.n === n) w.k++; else { w.n = n; w.k = 0; }
    return w.k >= 4;          // 같은 크기가 네 번 잇달아 나오면 다 그린 것이다
  }, null, { timeout: 60000, polling: 250 }).then(() => true, () => false);
  if (!drawn) {
    const d = await p.evaluate(() => ({
      성적표: (document.getElementById('app') || {}).innerHTML ? 1 : 0,
      오답수: (window.__fw || []).length,
      오답노트틀: !!document.getElementById('wrongbook'),
      카드자리: !!document.querySelector('[data-wb-cards]'),
      카드자리글자: ((document.querySelector('[data-wb-cards]') || {}).innerHTML || '').length,
      기다리는중표시: !!document.querySelector('[data-wb-loading]'),
      삼켜진오류: window.__rej || [],
    })).catch(e => ({ 못읽음: String(e).slice(0, 120) }));
    console.log('  FAIL  오답노트 카드가 60초 안에 안 그려졌다');
    console.log('        화면: ' + JSON.stringify(d, null, 0));
    console.log('        페이지 오류: ' + (errs.length ? errs.join(' | ') : '없음'));
    await ctx.close(); await browser.close(); srv.stop();
    process.exit(1);
  }

  const n = await p.evaluate(() => document.querySelectorAll('.wb-card').length);
  console.log(`\n오답 ${n}문항짜리 성적표\n`);

  /* ── #18 한 걸음 ────────────────────────────────────────────────── */
  console.log('── #18 0 뒤에 또 0 이 오지 않는다 ──');
  const step = await p.evaluate(() => {
    const el = document.querySelector('.onestep');
    if (!el) return null;
    const go = el.querySelector('.onestep__go');
    return { ey: (el.querySelector('.onestep__ey') || {}).textContent || '',
             q: (el.querySelector('.onestep__q') || {}).textContent || '',
             why: (el.querySelector('.onestep__why') || {}).textContent || '',
             go: !!go };
  });
  chk('한 걸음 칸이 있다', !!step, step ? step.ey.trim() : '(없다)');
  if (step) {
    chk('문항을 **하나만** 세운다', /^\s*\d+번/.test(step.q.trim()), step.q.trim().slice(0, 30));
    /* 근거 없이 «가장 빨리» 라고 하지 않는다 — 최상급을 쓰면 숫자가 같이 있어야 한다. */
    chk('«가장 빨리» 라고 할 때는 근거(또래 %)가 함께 있다',
        !/가장 빨리/.test(step.ey) || /\d+%/.test(step.why), true);
    chk('그 문항으로 내려가는 자리가 있다', step.go, true);
  }

  /* ── #19 사흘 ──────────────────────────────────────────────────── */
  console.log('\n── #19 한꺼번에 주지 않는다 ──');
  const bands = await p.evaluate(() =>
    [].slice.call(document.querySelectorAll('.wb-band')).map(e => e.textContent.trim()));
  chk('사흘로 나뉜다', bands.length === 3, bands.join(' · ') || '(안 나뉨)');
  chk('첫 띠가 «오늘 여기까지» 를 말한다', /오늘/.test(bands[0] || ''), bands[0] || '');

  /* ── #20 다시 풀었음 ───────────────────────────────────────────── */
  console.log('\n── #20 스스로 세는 자리 ──');
  const before = await p.evaluate(() => ({
    btns: document.querySelectorAll('.wb-redo').length,
    prog: (document.getElementById('wbProg') || {}).textContent || ''
  }));
  chk('문항마다 «다시 풀었음» 이 있다', before.btns === n, before.btns + '개');
  chk('몇 개 했는지 보인다', /0\s*\/\s*\d+/.test(before.prog.replace(/\s+/g, ' ')),
      before.prog.trim());

  await p.evaluate(() => document.querySelector('.wb-redo').click());
  const after = await p.evaluate(() => ({
    on: document.querySelector('.wb-redo').getAttribute('aria-pressed'),
    prog: (document.getElementById('wbProg') || {}).textContent || '',
    keys: Object.keys(localStorage).filter(k => k.indexOf('final:redone:') === 0)
  }));
  chk('누르면 세어진다', after.on === 'true' && /1\s*\/\s*\d+/.test(after.prog.replace(/\s+/g, ' ')),
      after.prog.trim());
  /* ⚠ 여기가 이 검사의 급소다. 이 표시가 시트로 가면 그건 **숙제 검사**가 된다.
     선생님께 보고되는 순간 학생이 스스로 세는 자리가 아니게 된다. */
  chk('이 브라우저에만 남는다 (시트로 안 간다)', after.keys.length === 1, after.keys.join(','));

  /* ── #27 난이도 ────────────────────────────────────────────────── */
  console.log('\n── #27 난이도가 보인다 ──');
  const peer = await p.evaluate(() => {
    const hs = [].slice.call(document.querySelectorAll('.wb-peer-h'));
    return { n: hs.length,
             txt: hs.slice(0, 1).map(e => e.textContent.replace(/\s+/g, ' ')).join(''),
             /* 분포 막대가 있으면 숫자가 있어야 한다 — 빈 막대 넷은 "아무도 안
                골랐다" 로 읽힌다. 모르는 것을 0% 로 그리면 거짓말이다. */
             emptyBars: [].slice.call(document.querySelectorAll('.wb-peer'))
               .filter(b => b.querySelector('.wb-orow') &&
                            [].slice.call(b.querySelectorAll('.op'))
                              .every(o => /^0%$/.test(o.textContent.trim()))).length };
  });
  chk('오답마다 난이도(또래 정답률)가 붙는다', peer.n === n, peer.n + '/' + n);
  chk('정답률 숫자가 실제로 적힌다', /\d+%/.test(peer.txt), peer.txt.slice(0, 60));
  chk('빈 막대만 있는 분포는 안 그린다', peer.emptyBars === 0,
      peer.emptyBars ? peer.emptyBars + '곳' : true);

  /* ── #23 목차로 갈 때 무엇을 들고 가나 ─────────────────────────── */
  console.log('\n── #23 어느 영역부터 ──');
  const link = await p.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2018');
    return shareLinkFinal(ex, sel, '홍길동');
  });
  const url = link.replace(/^https?:\/\/[^/]+\//, `http://localhost:${PORT}/`);
  const p2 = await ctx.newPage();
  p2.on('pageerror', e => errs.push(String(e).slice(0, 90)));
  await p2.goto(url, { waitUntil: 'load' });
  await p2.waitForFunction(() => !!document.querySelector('.fhero'), null, { timeout: 30000 });
  const a = await p2.$('a[href*="lecture-index"]');
  const [np] = await Promise.all([ctx.waitForEvent('page').catch(() => null),
                                  a.click().catch(() => {})]);
  const t = np || p2;
  await t.waitForLoadState('load').catch(() => {});
  const idx = await t.evaluate(() => ({
    search: location.search,
    weak: (document.querySelector('.weakfirst') || {}).textContent || '',
    chips: document.querySelectorAll('.weakfirst__list a').length,
    areas: document.querySelectorAll('section.area').length
  }));
  chk('목차 주소에 영역이 실린다', /[?&]w=/.test(idx.search), true);
  /* ⚠ 점수는 안 보낸다 — 목차는 남이 열어 볼 수 있는 장이다. */
  chk('점수는 안 실린다', !/score|pct|correct/.test(idx.search), true);
  chk('«여기부터» 가 뜬다', /여기부터/.test(idx.weak), idx.chips + '개 영역');
  chk('영역 이름이 실제로 맞아 붙는다 (띄어쓰기가 달라도)', idx.chips >= 2,
      idx.chips + '개');
  /* 목차의 차례는 개념이 쌓이는 차례다. 뒤섞으면 다음에 열었을 때 길을 잃는다. */
  chk('목차 자체는 안 뒤섞는다', idx.areas === 16, idx.areas + '개 영역 그대로');
  if (np) await np.close();

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n틀린 것이 «오늘 이걸 하면 된다» 로 이어진다.');
  process.exit(fail ? 1 : 0);
})();
