/* ============================================================
   **학부모가 걷는 길**을 그대로 걸어 본다 (브라우저 필요)
   ------------------------------------------------------------
   2026-08-10, 선생님 — *"한번더 학부모 관점에서 모든 페이지를 검수해줘"*.

   258장을 다 읽는 게 아니라, **문자를 받고 손가락이 갈 수 있는 곳**을 걷는다.
   걸어 보니 둘이 나왔다.

   ① 한 아이의 성적표가 **모든 학생 명단으로 가는 문**이었다

       학부모 링크(#r=…) 를 열면 암호를 안 묻는다 — 그건 맞다, 그 주소가
       열쇠다. 그런데 화면에 `‹ 시험 목록` 단추가 그대로 있었고, 그것을
       누르면 해시가 비면서 **선생님 콘솔이 암호 없이** 열렸다.

           명단 관리 ⚙ · 시트에서 불러오기 ↓ · 학생 제출 링크 복사 ⧉
           통합관리 ⌂ (DT·KMChC 까지) · 백업 내려받기 ↓

       암호 검사는 **열 때 한 번만** 돌기 때문이다. 학부모가 나쁜 마음을
       먹어야 열리는 것도 아니었다 — 단추가 눈에 보였다.

   ② 들어가면 **못 돌아 나오는 화면**이 둘 있었다

       강의 한 장(lec-*)에는 `‹ 성적표로` 가 진작 있었는데,
       **개념강의 목차**와 **해설지**에는 없었다. 학부모는 휴대폰으로 연다.
       화면 안에 길이 없으면 거기서 끝난다.

   여기서 지키는 것
   ----------------
     · 학부모 화면에 **선생님 문이 안 보인다**(시험 목록 · 공유용 HTML 저장)
     · 성적표 밖으로 나가면 **문고리를 다시 건다**
     · 성적표에서 나가는 세 갈래(목차 · 해설 · 강의)가 모두
       **자기 성적표로 돌아온다**

   ⚠ 문고리는 자물쇠가 아니다(final.html 의 gate 주석). 이 검사가 지키는 것은
     "잠갔다" 가 아니라 **"학부모에게 그 문을 보여 주지 않는다"** 이다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/parent-walk.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(180);

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}/`;

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

(async () => {
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}));

  /* ── 선생님이 성적표 링크를 만든다 ────────────────────────────── */
  let ctx = await browser.newContext({ serviceWorkers: 'block' });
  await ctx.route('**://script.google.com/**', r => r.abort());
  let p = await ctx.newPage(); p.on('pageerror', () => {});
  await p.goto(BASE + 'final.html', { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
    null, { timeout: 30000 });
  const link = await p.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2017'); openExam('hwol-2017');
    let ok = 0;
    for (let q = 1; q <= ex.nQ; q++) {
      if (q > 45) { setAns(q, 0); continue; }
      if (ok < 26) { setAns(q, ex.key[q - 1]); ok++; } else setAns(q, (ex.key[q - 1] % 4) + 1);
    }
    return shareLinkFinal(ex, sel, '박하람');
  });
  await ctx.close();
  const url = link.replace(/^https?:\/\/[^/]+\//, BASE);

  /* ── 학부모 기기: 아무 기록도 없는 새 브라우저 · 휴대폰 폭 ────── */
  ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block' });
  await ctx.route('**://script.google.com/**', r => r.abort());
  p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 90)));
  await p.goto(url, { waitUntil: 'load', timeout: 40000 });
  /* 고정 대기를 쓰지 않는다(tools/blind_wait.py). 성적표는 exams.json 을 받아
     온 뒤에 그려지므로, **그려졌다는 사실**을 기다린다.

     ⚠ 여기서 한 번 틀렸다(2026-08-11, main 이 빨간불). 처음에는 글자에
       `/해당|수상권|정답률/` 이 나오면 그려진 것으로 봤는데, 그 말은 **화면
       머리글에 이미 있다** — "파이널 · 수상권 진단". 그래서 exams.json 이
       늦게 오면 자가 **머리글만 있는 140자짜리 화면**을 성적표로 읽고 지나갔다.
       손에서는 파일이 즉시 와서 28,104자였고, CI 에서만 걸렸다.
       exams.json 을 6초 늦춰 그대로 재현했다.

       그래서 **성적표에만 있는 자리**(핵심 진단 히어로)를 기다리고, 길이도
       아래 검사와 같은 기준으로 함께 본다. 자가 재는 것과 자가 기다리는 것이
       달라지면, 자는 자기가 안 본 것을 통과시킨다. */
  const drawn = await p.waitForFunction(
    () => !!document.querySelector('.fhero') &&
          (document.body.innerText || '').length > 3000,
    null, { timeout: 30000 }).then(() => true).catch(() => false);
  if (!drawn) console.log('  (성적표가 30초 안에 안 그려졌다 — 아래 값이 그 증거다)');

  console.log('\n── 학부모가 문자 링크를 열었다 ──');
  const open = await p.evaluate(() => ({
    gate: !!document.getElementById('gate'),
    back: !!document.querySelector('button.back'),
    share: [...document.querySelectorAll('button')].some(b => /공유용/.test(b.textContent || '')),
    word: [...document.querySelectorAll('button')].some(b => /Word 저장/.test(b.textContent || '')),
    len: (document.body.innerText || '').length
  }));
  chk('성적표는 암호를 묻지 않는다 (주소가 열쇠다)', !open.gate, true);
  chk('성적표가 실제로 그려졌다', open.len > 3000, `(${open.len}자)`);
  chk('`‹ 시험 목록` 이 안 보인다 — 선생님 문이다', !open.back, true);
  chk('`공유용 HTML 저장` 이 안 보인다 — 선생님 단추다', !open.share, true);
  chk('`성적표 Word 저장` 은 그대로 있다 (학부모가 쓴다)', open.word, true);

  /* ── 언제 본 시험인지 (#17) ───────────────────────────────────────────
     발행일은 **파일을 만든 날**이라, 학부모가 두 달 뒤에 열면 오늘이 찍힌다.
     그래서 채점한 날을 링크에 싣는다.

     ⚠ **응시일은 아무 데도 기록돼 있지 않다.** 아는 것만 적는다 —
       모르는 것을 오늘 날짜로 메우면 틀린 것처럼 보이지 않으면서 틀린다. */
  const when = await p.evaluate(() => ({
    on: window.__gradedOn,
    line: (document.querySelector('#repPDF .muted') || {}).textContent || ''
  }));
  chk('링크에 채점일이 실려 온다', /^\d{4}-\d{2}-\d{2}$/.test(when.on || ''), when.on || '(없다)');
  chk('그 날짜가 화면에 적힌다', when.on ? when.line.includes(when.on) : false,
      when.line.trim());
  chk('응시일이라고는 안 적는다 (기록에 없다)', !/응시일/.test(when.line), true);

  /* 옛 링크에는 이 칸이 없다. **그때는 아무 말도 안 해야 한다.** */
  const oldUrl = url.replace(/[#&]t=\d{8}&/, m => m[0] === '#' ? '#' : '&');
  const op = await ctx.newPage();
  op.on('pageerror', e => errs.push(String(e).slice(0, 90)));
  await op.goto(oldUrl, { waitUntil: 'load' });
  await op.waitForFunction(() => !!document.querySelector('.fhero'), null, { timeout: 30000 })
    .catch(() => {});
  const oldLine = await op.evaluate(() => ({
    on: window.__gradedOn,
    line: (document.querySelector('#repPDF .muted') || {}).textContent || ''
  }));
  chk('옛 링크는 그대로 열린다', /\S/.test(oldLine.line), oldLine.line.trim());
  chk('옛 링크에 없는 날짜를 지어내지 않는다', !oldLine.on && !/채점/.test(oldLine.line), true);
  await op.close();

  /* ── 성적표 밖으로 나가면 문고리를 다시 거는가 ────────────────── */
  await p.evaluate(() => { location.hash = ''; });
  const outside = await p.waitForSelector('#gate', { timeout: 15000 })
    .then(() => true).catch(() => false);
  chk('성적표 밖으로 나가면 다시 코드를 묻는다', outside, true);

  /* ── 세 갈래가 모두 자기 성적표로 돌아오는가 ──────────────────────
     ⚠ **새 창에서 건는다.** 바로 위에서 문고리를 시험하느라 이 창에는 암호
       화면이 덮여 있다. 그 위에서 링크를 누르면 덮개가 눌린다 — 검사가
       화면을 못 만지는 것을 '길이 없다' 로 잘못 읽는다(실제로 한 번 그랬다). */
  await p.close();
  p = await ctx.newPage();
  p.on('pageerror', e => errs.push(String(e).slice(0, 90)));
  console.log('\n── 성적표에서 나가는 세 갈래 ──');
  for (const [sel, name] of [['a[href*="lecture-index"]', '개념강의 목차'],
                             ['a[href*="sol-final"]', '해설지'],
                             ['a[href*="lec-1"]', '개념 강의']]) {
    await p.goto(url, { waitUntil: 'load' });
    /* ⚠ 여기도 머리글에 걸렸다. `a[href*="lec-"]` 는 화면 꼭대기의
       `개념강의 목차 →` 에도 맞으므로, 성적표가 안 그려져도 통과한다.
       위와 같이 **성적표에만 있는 자리**를 기다린다. */
    await p.waitForFunction(() => !!document.querySelector('.fhero'),
      null, { timeout: 30000 }).catch(() => {});
    const a = await p.$(sel);
    if (!a) { chk(`${name} 로 가는 링크가 있다`, false, '(못 찾음)'); continue; }
    const [np] = await Promise.all([
      ctx.waitForEvent('page').catch(() => null),
      a.click().catch(() => {})
    ]);
    const t = np || p;
    await t.waitForLoadState('load').catch(() => {});
    await t.waitForSelector('a.back', { timeout: 10000 }).catch(() => {});
    const r = await t.evaluate(() => {
      const b = document.querySelector('a.back');
      return { url: location.href, t: b ? (b.textContent || '').trim() : null,
               h: b ? b.href : null };
    });
    chk(`${name} · 돌아올 자리가 주소에 실린다`, /\?from=/.test(r.url), true);
    chk(`${name} · 화면 안에 돌아가는 길이 있다`, !!r.t, r.t ? `"${r.t}"` : '(없다)');
    /* ⚠ `#r=` 를 글자 그대로 보면 안 된다. 해시 앞에는 또래 통계(`s=`)와
       채점일(`t=`)이 붙을 수 있어서 `#t=…&r=…` 이 된다 — 실제 문고리는
       처음부터 `[#&]r=` 로 보고 있었는데(tools/gen_sol_page.py) 이 자만
       좁게 보다가, #17 을 넣자마자 셋이 한꺼번에 빨간불이 났다.
       **자가 코드보다 좁으면, 코드가 자란 날 자가 먼저 운다.** */
    chk(`${name} · 그 길이 자기 성적표를 가리킨다`, /[#&]r=/.test(r.h || ''), true);
    if (np) await np.close();
  }

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n학부모가 걷는 길이 막히지도, 남의 자리로 새지도 않는다.');
  process.exit(fail ? 1 : 0);
})();
