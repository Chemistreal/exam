/* ============================================================
   **채점하다 자리를 옮기면 입력이 날아가는가** (브라우저 필요)
   ------------------------------------------------------------
   2026-08-11, 선생님 결정 #28 — *"채점 중 실수로 뒤로 가면 입력이 날아가는지
   안 재 봤다"*. `tests/grading-input.js` 는 **갈아엎힘**(다른 곳에서 온 자료가
   치는 중인 화면을 덮는 것)만 본다. 손이 미끄러지는 쪽은 아무도 안 쟀다.

   선생님은 한 회차를 앉아서 서른 명쯤 친다. 60문항을 다 넣고 마지막 한 칸을
   남겼을 때 뒤로가기가 눌리면, 다시 처음부터다. 그런 일이 한 번만 있어도
   그 앱은 못 믿는 앱이 된다.

   여기서 걸어 보는 세 갈래
   ------------------------
     ① **뒤로가기** — 브라우저 뒤로가기(해시가 바뀐다)
     ② **새로고침** — 실수로 F5, 또는 폰이 화면을 되살릴 때
     ③ **시험 목록으로** — 화면 안의 단추를 잘못 누름

   무엇을 지키자는 것인가
   ----------------------
   «절대 안 날아간다» 를 요구하지 않는다. 웹에서 새로고침을 완전히 막을 수는
   없고, 막는 것이 옳지도 않다. **묻지도 않고 날아가지 않는 것**이 규칙이다 —
   나가려 할 때 한 번 붙잡거나, 돌아왔을 때 치던 것이 그대로 있거나.

   ⚠ 이 자는 **고치라고 하지 않는다.** 지금 어떻게 되는지 적어 두고, 그 상태가
     **나빠지면** 빨간불이다. 어떻게 붙잡을지는 선생님이 정할 칸이다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/grading-lost.js
   ============================================================ */
'use strict';
const path = require('path');
const { serve } = require('./_serve.js');

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

const HALF = 30;   // 60문항 가운데 서른 칸을 채운 상태에서 사고가 난다

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  await ctx.route('**://script.google.com/**', r => r.abort());
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 90)));

  /* 물음은 **한 자리에서만** 받는다. `p.once` 를 덧붙이면 같은 물음을 둘이
     받아 "이미 처리된 물음" 으로 터진다(그렇게 한 번 터뜨렸다).
     받은 말을 적어 두고, 무엇을 물었는지는 그 글에서 가른다. */
  let asked = 0;
  const said = [];
  p.on('dialog', async d => { asked++; said.push(String(d.message() || '')); await d.accept(); });

  async function fillHalf() {
    await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
    /* ⚠ FINAL_EXAMS 가 생긴 것과 **시동이 끝난 것은 다르다.**
       start() 는 「시험 목록 로드 → 기준 기록 로드 → boot()」 차례인데,
       시험 목록만 보고 달려들면 몇십 ms 뒤에 도착한 boot() 이 목록 화면을
       그리며 cur·sel 을 지운다 — 친 30칸이 증발하고, 나가기 물음은 잡을
       것이 없다고 본다. 스물다섯 판에 서너 번꼴로 그렇게 흔들렸다
       (2026-08-11, 부른 기록: openExam → 39ms 뒤 boot → renderList).
       실제 사람은 이 경주를 못 만난다 — boot 전엔 화면에 누를 것이 없다.
       그러니 사람처럼 **목록이 화면에 그려질 때까지** 기다린다. */
    await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length &&
      !!document.querySelector('#app .card'),
      null, { timeout: 30000 });
    const n = await p.evaluate((half) => {
      /* 유령 잡기 2 — 화면을 그리는 함수의 **호출 자체**를 남긴다.
         function 선언은 window 에 붙으므로 감쌀 수 있다. Date.now 로 적어
         판을 건너도 차례가 보인다. 판정에는 안 쓴다. */
      if (!window.__callTap) {
        window.__callTap = 1;
        ['renderList', 'openExam', 'leaveList', 'refreshScreen', 'boot', 'scoreAuto'].forEach(function (fn) {
          var orig = window[fn];
          if (typeof orig !== 'function') return;
          window[fn] = function () {
            try {
              var log = JSON.parse(localStorage.getItem('__test_calls') || '[]');
              log.push({ t: Date.now() % 1000000, f: fn,
                누가: String(new Error().stack || '').split('\n').slice(2, 4)
                  .map(function (x) { return x.trim().replace(/^at /, '').replace(/https?:\/\/[^)\s]*\//g, ''); })
                  .join(' ← ') });
              localStorage.setItem('__test_calls', JSON.stringify(log.slice(-30)));
            } catch (_) {}
            return orig.apply(this, arguments);
          };
        });
        try {
          var log0 = JSON.parse(localStorage.getItem('__test_calls') || '[]');
          log0.push({ t: Date.now() % 1000000, f: '(fillHalf 시작)' });
          localStorage.setItem('__test_calls', JSON.stringify(log0.slice(-30)));
        } catch (_) {}
      }
      openExam('hwol-2017');
      document.getElementById('nm').value = '홍길동';
      const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2017');
      for (let q = 1; q <= half; q++) setAns(q, ex.key[q - 1]);
      return Object.keys(sel).filter(k => sel[k]).length;
    }, HALF);
    /* ⚠ 「나가시겠습니까」 물음이 실제로 뜨는지는 **브라우저 재량**이다.
       Chrome 은 사람 손길(user activation)이 없으면 물음을 조용히 건너뛸 수
       있고, 이 검사는 답안을 전부 스크립트로 넣으니 손길이 0번이다. 재어
       보니 열다섯 판에서 앱의 처리기는 15번 다 돌았는데 물음은 12번만 떴다
       (2026-08-11) — 자가 앱이 아니라 **브라우저의 기분**을 재고 있었다.

       앱이 할 수 있는 것은 막겠다고 손을 드는 것(preventDefault)까지다.
       그래서 그 손을 들었는지를 적어 둔다. 앱의 자리(1763줄)가 먼저 등록돼
       있어 이 청취자는 그 뒤에 돌고, e.defaultPrevented 로 앱이 손을
       들었는지 보인다. 물음이 뜨면 그것대로 세고(asked), 안 떠도 손을
       들었으면 앱은 제 몫을 다 한 것이다. */
    await p.evaluate(() => {
      localStorage.setItem('__test_bu', '');
      addEventListener('beforeunload', (e) => {
        /* '1' = 앱이 막으려 손을 들었다 · '0:…' = 이벤트는 왔는데 앱이 잡을
           것이 없다고 봤다(그때의 더러움 상태를 같이 적는다) · '' = 이벤트
           자체가 안 왔다. 셋을 갈라야 다음에 갈 곳이 보인다. */
        try {
          var why = '';
          if (!e.defaultPrevented) {
            try {
              why = ':cur=' + !!window.cur + ' 칸=' +
                (typeof sel !== 'undefined' ? Object.keys(sel).filter(function(k){ return sel[k]; }).length : '?') +
                ' 이름=' + JSON.stringify(((document.getElementById('nm') || {}).value || ''));
            } catch (_) { why = ':?'; }
          }
          localStorage.setItem('__test_bu', e.defaultPrevented ? '1' : '0' + why);
        } catch (_) {}
      });
      /* 유령 잡기 — #app 이 다시 그려질 때마다 누가(스택) 그렸는지를
         localStorage 에 남긴다. 화면이 떠나도 기록은 남는다.
         판정에는 안 쓴다. 실패했을 때만 읽는다. */
      if (!window.__tapOn) {
        window.__tapOn = 1;
        const app = document.getElementById('app');
        const d = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
        Object.defineProperty(app, 'innerHTML', {
          get() { return d.get.call(this); },
          set(v) {
            try {
              const log = JSON.parse(localStorage.getItem('__test_renders') || '[]');
              log.push({
                t: Math.round(performance.now()),
                누가: String(new Error().stack || '').split('\n').slice(1, 4)
                       .map(x => x.trim().replace(/^at /, '').replace(/https?:\/\/[^)\s]*\//g, ''))
                       .join(' ← '),
                앞부분: String(v).replace(/\s+/g, ' ').slice(0, 60),
              });
              localStorage.setItem('__test_renders', JSON.stringify(log.slice(-40)));
            } catch (_) {}
            return d.set.call(this, v);
          },
        });
      }
    });
    return n;
  }

  /* 나간 뒤, 앱이 잡으려 손을 들었었는지(위 fillHalf 의 기록)를 읽는다.
     나간 화면(about:blank)에는 이 저장소가 없어서 새 화면으로 잠깐 연다. */
  async function heldHand() {
    const p2 = await ctx.newPage();
    try {
      await p2.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'domcontentloaded', timeout: 20000 });
      const raw = await p2.evaluate(() => localStorage.getItem('__test_bu'));
      if (raw !== '1') console.log('        (손 기록: ' + JSON.stringify(raw) + ')');
      return raw === '1';
    } catch (e) { return false; }
    finally { await p2.close().catch(() => {}); }
  }

  /* ── 초를 세지 않는다 ────────────────────────────────────────────────
     나간 뒤 화면은 둘 중 하나로 자리를 잡는다 — **채점 화면**(이름 칸이 있다)
     이거나 **시험 목록**(회차 카드가 있다). 그 둘 중 하나가 될 때까지 기다린다.
     400ms 를 세면 느린 기계에서는 모자라고 빠른 기계에서는 버린다
     (tools/blind_wait.py — 이 자도 처음엔 그러다 천장에 걸렸다). */
  const settled = () => p.waitForFunction(
    () => !!document.getElementById('nm') ||
          !!document.querySelector('.card') ||
          !!document.querySelector('.fhero'),
    null, { timeout: 20000 }).catch(() => {});

  function typed() {
    return p.evaluate(() => {
      /* 화면에 실제로 칠해져 있는 칸을 센다 — 기억(sel)이 아니라 **보이는 것**을
         본다. 선생님이 보는 것이 그것이다. */
      const marked = document.querySelectorAll('.omr .on, .omr [aria-checked="true"], .opt.on').length;
      const inMem = (typeof sel !== 'undefined')
        ? Object.keys(sel).filter(k => sel[k]).length : 0;
      const name = (document.getElementById('nm') || {}).value || '';
      const grading = !!document.getElementById('nm');
      return { marked, inMem, name, grading };
    });
  }

  console.log('\n── 60문항 가운데 ' + HALF + '칸을 쳤다 ──');
  const n0 = await fillHalf();
  chk('친 것이 화면에 들어갔다', n0 === HALF, n0 + '칸');

  console.log('\n── ① 뒤로가기를 눌렀다 ──');
  asked = 0;
  await p.goBack({ waitUntil: 'load' }).catch(() => {});
  await settled();
  let r = await typed();
  /* 물음이 안 떠도, 앱이 막겠다고 손을 들었으면(위 fillHalf) 앱의 몫은 다
     한 것이다 — 물음을 띄울지는 브라우저가 정하고, 사람 손길이 있는 실제
     화면에서는 띄운다. */
  let held = (r.grading || asked > 0) ? false : await heldHand();
  chk('뒤로가기 뒤 — 화면이 남거나, 물었거나, 앱이 잡으려 손을 들었다',
      r.grading || asked > 0 || held,
      r.grading ? `그대로 (${r.inMem}칸)` : (asked ? '물었다'
        : (held ? '손은 들었다 (물음은 브라우저 재량)' : '**잡으려는 손짓조차 없었다**')));

  console.log('\n── ② 새로고침을 눌렀다 ──');
  await fillHalf();
  asked = 0;
  await p.reload({ waitUntil: 'load' }).catch(() => {});
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
    null, { timeout: 30000 }).catch(() => {});
  await settled();
  r = await typed();
  held = (r.grading || asked > 0) ? false : await heldHand();
  chk('새로고침 뒤 — 화면이 남거나, 물었거나, 앱이 잡으려 손을 들었다',
      r.grading || asked > 0 || held,
      r.grading ? `그대로 (${r.inMem}칸)` : (asked ? '물었다'
        : (held ? '손은 들었다 (물음은 브라우저 재량)' : '**잡으려는 손짓조차 없었다**')));

  console.log('\n── ③ 시험 목록 단추를 잘못 눌렀다 ──');
  await fillHalf();
  asked = 0;
  await p.evaluate(() => { const b = document.querySelector('button.back'); if (b) b.click(); });
  await settled();
  r = await typed();
  chk('목록으로 나간 뒤 — 치던 화면이 남거나, 나가기 전에 물었다',
      r.grading || asked > 0,
      r.grading ? `그대로 (${r.inMem}칸)` : (asked ? '물었다' : '**묻지도 않고 날아갔다**'));

  /* ── 붙잡는 것보다 중요한 것: **돌아왔을 때 그대로 있는가** ──────────
     묻기만 하고 안 남기면, 실수로 «예» 를 누른 순간 다 날아간다.
     한 번 나갔다가 같은 회차를 다시 열어 «이어서 하기» 를 고른다. */
  console.log('\n── 나갔다가 같은 회차를 다시 열었다 ──');
  await fillHalf();
  const before = await typed();
  await p.evaluate(() => { location.hash = ''; renderList(); });   // 물음 없이 강제로 나간다
  await p.waitForFunction(() => !!document.querySelector('.card'), null, { timeout: 20000 });

  said.length = 0;
  await p.evaluate(() => openExam('hwol-2017'));
  /* 되살리기는 화면을 다 그린 **뒤에** 채운다. 그러니 «칸이 생겼다» 로는
     모자라고, 채워졌거나 물음이 왔을 때까지 본다. */
  await p.waitForFunction(() => !!document.getElementById('ai_1') &&
    (typeof sel !== 'undefined') && Object.keys(sel).filter(k => sel[k]).length > 0,
    null, { timeout: 20000 }).catch(() => {});
  const after = await typed();
  chk('다시 열면 이어서 할지 묻는다', said.some(m => /이어서/.test(m)),
      said[0] ? said[0].split('\n')[0] : '(안 물었다)');
  chk('친 것이 그대로 돌아온다', after.inMem === before.inMem,
      `${before.inMem}칸 → ${after.inMem}칸`);
  chk('이름도 그대로 돌아온다', after.name === before.name, `"${after.name}"`);

  /* 채점이 끝나면 지워야 한다 — 안 지우면 다음 학생 칸에 앞사람 답이 뜬다.
     그건 살려 주는 게 아니라 **틀린 채점을 만드는 것**이다. */
  console.log('\n── 채점을 끝낸 뒤 다음 학생 ──');
  await p.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2017');
    for (let q = 1; q <= ex.nQ; q++) setAns(q, ex.key[q - 1]);
    document.getElementById('nm').value = '홍길동';
    scoreAuto();
  });
  /* 채점이 끝나 성적표가 그려질 때까지 — 그때 치다 만 것이 지워진다. */
  await p.waitForFunction(() => !!document.querySelector('.fhero'), null, { timeout: 30000 });
  said.length = 0;
  await p.evaluate(() => openExam('hwol-2017'));
  await p.waitForFunction(() => !!document.getElementById('ai_1'), null, { timeout: 20000 });
  const fresh = await typed();
  const askedAgain = said.some(m => /이어서/.test(m));
  chk('앞사람 답이 다음 학생 칸에 안 떠 있다', fresh.inMem === 0 && !askedAgain,
      `${fresh.inMem}칸` + (askedAgain ? ' · 또 물었다(지워졌어야 한다)' : ''));

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  /* 실패했을 때만 — 화면을 누가 언제 다시 그렸는지, 물음은 무엇이 왔는지. */
  if (fail) {
    try {
      const p3 = await ctx.newPage();
      await p3.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const renders = await p3.evaluate(() => localStorage.getItem('__test_renders') || '[]');
      const calls = await p3.evaluate(() => localStorage.getItem('__test_calls') || '[]');
      console.log('\n다시 그린 기록: ' + renders);
      console.log('\n부른 기록: ' + calls);
      await p3.close();
    } catch (e) { console.log('\n다시 그린 기록을 못 읽었다: ' + String(e).slice(0, 80)); }
    console.log('물음 기록: ' + JSON.stringify(said.map(m => m.split('\n')[0])));
  }

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건 — 치던 것이 묻지도 않고 날아가는 자리가 있다.`
    : '\n치던 것이 묻지도 않고 날아가는 자리는 없다.');
  process.exit(fail ? 1 : 0);
})();
