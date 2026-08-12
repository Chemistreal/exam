/* ============================================================
   **시트에 쓰는 일은 조용히 하지 않는다** (브라우저 필요)
   ------------------------------------------------------------
   2026-08-12, 선생님이 물으셨다 — *"이런애들 지금 시험 안봤는데 왜
   올라가있어?"* 학원 시트에 오늘 날짜로 넉 줄이 있었다. 이름·학교·점수가 다
   진짜고, 1초 간격이었다. 그날 선생님이 채점한 것은 **2019 뿐**이었다.

   무슨 일이었나
   -------------
   파이널은 채점할 때 `up:0`(보냈지만 닿았는지 모름)을 달아 둔다. 망이 끊긴 채
   채점한 기록이 이 브라우저에만 남아 사라지는 것을 막는 유일한 장치다.
   그리고 앱을 열 때마다 자동으로 시트와 맞추면서(`autoSync`), 시트에 안 보이는
   `up:0` 기록을 **다시 보낸다**(`resendPending`).

   그 자는 **지금 보는 회차만이 아니라 모든 회차를 돈다.** 그래서 2019 를
   채점하려고 앱을 연 순간, 그 브라우저에 남아 있던 **2018 의 미확인 넉 건**이
   시트로 나갔다. 오늘 날짜가 찍힌 채로.

   앱이 정해진 대로 한 일이다. 잘못은 **아무 말도 안 한 것**이었다 —
   «다시 올린 N건» 이 `if(!quiet)` 안에 있었고 자동 맞춤은 늘 `quiet` 이라,
   시트에 줄이 생기는 동안 화면은 조용했다.

   어떻게 정했나
   -------------
   선생님 말씀: *"기능 자체를 없애면 되지 않아? 처음에 입력하면 바로 보내고
   끝!"* — 앱이 **사람 모르게** 시트를 고치는 것이 뿌리라는 말씀이 옳다.

   다만 통째로 없애면 **못 간 것이 조용히 사라진다.** no-cors 라 갔는지 알 수가
   없어서, 안 간 기록은 그 브라우저에만 남는다. 브라우저를 비우면 없어지고
   아무도 모른다.

   그래서 **자동은 끄고, 사람이 누르면 보낸다**(선생님 결정 2026-08-12).

   여기서 지키는 것
   ----------------
     · 열기만 해서는 시트에 **한 글자도 안 쓴다** — 놀랄 일이 없다
     · 못 간 것이 있으면 화면이 **몇 건인지 말한다**
     · 사람이 «지금 맞춰 보기» 를 누르면 그때 보내고, **무엇을 보냈는지 말한다**

   **읽는 것은 조용해도 되고, 쓰는 것은 안 된다.**

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/silent-resend.js
   ============================================================ */
'use strict';
const path = require('path');
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH;
const ROOT = path.join(__dirname, '..');
let PORT = Number(process.env.PORT || 0);
const OTHER = 'hwol-2018';        // 오늘 채점하지 않은 회차

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
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  const ctx = await browser.newContext({ serviceWorkers: 'block' });

  /* NOSHEET-예외: 이 검사는 **나가는 POST 를 세는 것**이 목적이라, 창구를
     `_nosheet` 로 덮으면 셀 것이 사라진다. 대신 script.google* 를 통째로
     가로채 **전부 끊는다** — 진짜 시트에는 한 글자도 안 나간다.
     (`tools/test_nosheet.py` 가 이 표시와 실제로 막는 자리를 같이 본다)

     ⚠ 여기서는 `_nosheet` 를 그대로 쓰지 않는다. 이 검사가 보려는 것이
     **시트로 나가는 POST 그 자체**라서, 답은 주되 나가는 것은 세어야 한다.
     그래도 진짜 시트에는 한 글자도 안 나간다 — 모두 가로채서 끊는다. */
  const posts = [];
  await ctx.route('**://script.google*.com/**', r => {
    const req = r.request();
    if (req.method() === 'POST') { posts.push(req.url()); return r.abort(); }
    const cb = new URL(req.url()).searchParams.get('callback') || 'cb';
    /* 시트가 «아무것도 없다» 고 답한다 → 미확인 기록이 안 보이므로 다시 보낸다. */
    return r.fulfill({ status: 200, contentType: 'text/javascript',
      body: cb + '(' + JSON.stringify({ ok: true, rows: [], students: [], classes: [],
        list: [], passed: [], pending: [], sent: [], snoozed: [], changed: 0 }) + ');' });
  });

  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 100)));

  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length
    && !!document.querySelector('#app .card'), null, { timeout: 30000 });

  /* 어제 채점했는데 시트에 닿았는지 모르는 기록 넷을 심는다(up:0). */
  const seeded = await p.evaluate((id) => {
    const ex = FINAL_EXAMS.find(e => e.id === id);
    const rows = ['가나다', '라마바', '사아자', '차카타'].map(nm => ({
      name: nm, school: 'ㅇㅇ중', grade: '2', ts: Date.now() - 86400000,
      correct: 40, total: ex.nQ, wrong: ex.nQ - 40,
      ans: Array.from({ length: ex.nQ }, (_, i) => ex.key[i]), up: 0, upTry: 0 }));
    localStorage.setItem('final:roster:' + cohortKey(id), JSON.stringify(rows));
    /* 사람에게 한 말을 모아 둔다. */
    window.__said = [];
    const f = window.fToast;
    window.fToast = function (m) { window.__said.push(String(m)); return f && f.apply(this, arguments); };
    return rows.length;
  }, OTHER);
  chk('어제 못 올린 기록 넷을 심었다', seeded === 4, seeded + '건');

  /* ── ① 다른 회차를 보러 열었을 뿐이다. 여기서 시트가 바뀌면 안 된다 ── */
  console.log('\n── 앱을 열었을 뿐이다 ──');
  await p.evaluate(() => autoSync(true));
  /* 자동 맞춤은 읽기는 한다 — 읽기가 끝날 때까지 기다린다(GET 이 돌아온 뒤). */
  await p.waitForFunction(() => window.__lastSync !== undefined || true, null, { timeout: 5000 })
    .catch(() => {});
  await p.waitForTimeout(3000);
  chk('시트에 **한 글자도 안 썼다**', posts.length === 0, posts.length + '건 나감');

  /* ── ② 못 간 것이 있으면 화면이 말한다 ── */
  console.log('\n── 못 간 것이 있다고 화면이 말한다 ──');
  const badge = await p.evaluate(() => {
    const el = document.querySelector('.pend');
    return el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
  });
  chk('«아직 안 올라간 기록» 을 세어 보여 준다', /아직 안 올라간 기록/.test(badge), badge.slice(0, 70));
  chk('몇 건인지 적는다', /4건/.test(badge), badge.slice(0, 70));
  chk('저절로 올라간다고 **거짓말하지 않는다**', !/저절로 올라갑니다/.test(badge), badge.slice(0, 90));
  chk('사람이 누를 자리가 있다', /지금 맞춰 보기/.test(badge), badge.slice(0, 90));

  /* ── ③ 사람이 누르면 그때 보내고, 무엇을 보냈는지 말한다 ── */
  console.log('\n── 사람이 «지금 맞춰 보기» 를 눌렀다 ──');
  await p.evaluate(() => { window.__said = []; syncAllFromSheet(); });
  await p.waitForFunction(() => (window.__said || []).some(m => /다시 올렸습니다/.test(m)),
    null, { timeout: 30000 }).catch(() => {});
  const said = await p.evaluate(() => window.__said || []);
  chk('그때는 실제로 나갔다', posts.length === 4, posts.length + '건');

  const tell = said.find(m => /다시 올렸습니다/.test(m)) || '';
  chk('무엇을 보냈는지 **말한다**', !!tell, tell || '(아무 말도 없었다)');
  chk('어느 회차인지 적는다', /2018/.test(tell), tell);
  chk('몇 건인지 적는다', /4건/.test(tell), tell);
  /* 선생님이 처음 겪은 혼란이 «오늘 시험 안 봤는데» 였다. 그 오해를 그
     자리에서 푼다 — 날짜만 보고 새 응시로 읽지 않게. */
  chk('오늘 채점한 것이 아니라고 알린다', /오늘 채점한 것이 아닙니다/.test(tell), tell);

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n열기만 해서는 시트가 안 바뀌고, 사람이 누르면 무엇을 보냈는지 말한다.');
  process.exit(fail ? 1 : 0);
})();
