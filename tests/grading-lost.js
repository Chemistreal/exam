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
    await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
      null, { timeout: 30000 });
    return p.evaluate((half) => {
      openExam('hwol-2017');
      document.getElementById('nm').value = '홍길동';
      const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2017');
      for (let q = 1; q <= half; q++) setAns(q, ex.key[q - 1]);
      return Object.keys(sel).filter(k => sel[k]).length;
    }, HALF);
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
  chk('뒤로가기 뒤 — 치던 화면이 남거나, 나가기 전에 물었다',
      r.grading || asked > 0,
      r.grading ? `그대로 (${r.inMem}칸)` : (asked ? '물었다' : '**묻지도 않고 날아갔다**'));

  console.log('\n── ② 새로고침을 눌렀다 ──');
  await fillHalf();
  asked = 0;
  await p.reload({ waitUntil: 'load' }).catch(() => {});
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
    null, { timeout: 30000 }).catch(() => {});
  await settled();
  r = await typed();
  chk('새로고침 뒤 — 치던 화면이 남거나, 나가기 전에 물었다',
      r.grading || asked > 0,
      r.grading ? `그대로 (${r.inMem}칸)` : (asked ? '물었다' : '**묻지도 않고 날아갔다**'));

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

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건 — 치던 것이 묻지도 않고 날아가는 자리가 있다.`
    : '\n치던 것이 묻지도 않고 날아가는 자리는 없다.');
  process.exit(fail ? 1 : 0);
})();
