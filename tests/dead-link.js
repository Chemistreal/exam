/* ============================================================
   **죽은 회차 링크는 말을 해야 한다** (브라우저 필요)
   ------------------------------------------------------------
   2026-08-21, 선생님 물음 — *"기존에 보냈던 링크나 이런건 그대로 접속도
   다 되고 잘 볼 수 있는거지?"*

   재어 보니 「누적 파이널」 여덟 개가 내려가 있었다(선생님 지시대로 지운
   것이다). 문제는 **지운 것** 이 아니라 **지워진 링크를 눌렀을 때** 였다.

     열린 화면: 「답안 제출 · 시험을 고르고 이름·학교·답안을 …」  ← 전체 목록
     오류: 없음

   자기 회차가 없어졌다는 말은 어디에도 없고, 학생 눈에는 그냥 시험 목록이
   뜬다. 여기서 학생이 하는 일은 뻔하다 — 비슷해 보이는 회차를 하나 골라
   60문항을 찍어 넣고 제출한다. 채점표에는 **엉뚱한 회차의 점수**가 남고,
   그게 조용해서 선생님도 며칠 뒤에나 안다. 임시 저장이 남아 있으면 더
   나빠서, 아예 **다른 회차가 저절로 열린다.**

   그런데 이 여덟 개는 사실 **되살릴 수 있다.** 주소에 실린 것이 학생 코드라,
   같은 코드의 변형본 60제(-2) · 실전 30제(-3) · 재도전 10제(-4) 는 그대로
   살아 있다. 그러니 «없다» 로 끝낼 자리가 아니라 «그 사람 시험» 을 세워 줄
   자리다 — 예전에 보낸 주소가 여전히 제 사람에게 닿는다.

   여기서 지키는 것
   ----------------
     · 내려간 누적 파이널로 들어오면 **그 학생의 살아 있는 회차**를 세운다
     · 아예 없는 회차면 **없다고 말한다** — 회차 이름을 짚어서
     · 그때 답안 칸을 세우지 않는다 — 고를 게 없어야 잘못 못 고른다
     · 임시 저장이 있어도 **다른 회차를 대신 열지 않는다**
     · 살아 있는 회차 링크는 예전 그대로 바로 열린다(막다가 막지 말 것)
     · **망이 미끄러졌을 때 살아 있는 링크를 죽었다고 하지 않는다** — 회차
       목록을 못 받은 것과 회차가 없는 것은 학생에게 정반대의 뜻이다

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/dead-link.js
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

/* 실제로 지워진 회차 하나. 선생님이 카톡으로 보냈던 주소 그대로다. */
const DEAD = 's4w000h6h6l0';

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 120)));

  const open = async (q) => {
    await p.goto(`http://localhost:${PORT}/final-submit.html${q}`,
      { waitUntil: 'load', timeout: 40000 });
    await p.waitForFunction(() => !!document.querySelector('#app .card, #app .exlist'),
      null, { timeout: 30000 });
    return p.evaluate(() => ({
      text: (document.getElementById('app') || {}).textContent || '',
      /* 답안/이름 칸이 서 있으면 «시험이 열린» 것이다. */
      form: !!document.getElementById('nm'),
      list: !!document.querySelector('.exlist'),
      cur: (typeof cur !== 'undefined' && cur) ? cur.id : null,
      alt: document.querySelectorAll('#app .card .exlist .exbtn').length,
      altIds: [].map.call(document.querySelectorAll('#app .card .exlist .exbtn'),
        b => ((b.getAttribute('onclick') || '').match(/'([^']+)'/) || [])[1] || ''),
    }));
  };

  /* ── ① 내려간 「누적 파이널」 링크 — 그 사람 시험으로 이어 준다 ── */
  console.log('── 내려간 누적 파이널 주소로 들어온다 ──');
  let r = await open('?exam=' + DEAD);
  chk('내려갔다고 말한다', /내려갔습니다/.test(r.text),
    r.text.replace(/\s+/g, ' ').slice(0, 60));
  chk('본인 시험을 바로 세워 준다', r.alt >= 1, r.alt + '개');
  chk('세워 준 것이 전부 그 사람 회차다', r.altIds.length > 0
    && r.altIds.every(id => id.indexOf(DEAD + '-') === 0), r.altIds.join(' '));
  chk('답안 칸을 멋대로 열지 않는다', !r.form, r.cur || '열린 회차 없음');

  /* ── ①-2 아예 없는 회차 — 고르지 말라고 한다 ── */
  console.log('\n── 아예 없는 회차로 들어온다 ──');
  const NONE = 'zzzz0no0such0';
  r = await open('?exam=' + NONE);
  chk('없어졌다고 말한다', /찾지 못했습니다/.test(r.text),
    r.text.replace(/\s+/g, ' ').slice(0, 60));
  chk('어느 회차인지 짚는다', r.text.indexOf(NONE) >= 0);
  chk('아무거나 고르지 말라고 한다', /아무거나 고르지 마세요/.test(r.text));
  chk('답안 칸을 세우지 않는다', !r.form, r.cur || '열린 회차 없음');

  /* ── ② 임시 저장이 남아 있어도 남의 회차를 열지 않는다 ── */
  console.log('\n── 쓰다 만 답안이 남아 있는 채로 죽은 링크를 누른다 ──');
  const live = await p.evaluate(() => (STUDENT_FINALS.concat(FINAL_EXAMS)
    .filter(e => !e.hidden || e.id.indexOf('-') > 0)[0] || {}).id);
  await p.evaluate((id) => {
    localStorage.setItem('chemistreal:finalsubmit:draft:' + id,
      JSON.stringify({ sel: { 1: 3, 2: 1 }, ts: Date.now() }));
  }, live);
  r = await open('?exam=' + NONE);
  chk('임시 저장이 있어도 다른 회차가 안 열린다', !r.form && r.cur === null,
    r.cur || '열린 회차 없음');
  chk('그래도 없어졌다고 말한다', /찾지 못했습니다/.test(r.text));

  /* ── ③ 살아 있는 링크는 예전 그대로 ── */
  console.log('\n── 살아 있는 회차 링크 ──');
  r = await open('?exam=' + live);
  chk('바로 열린다', r.form && r.cur === live, r.cur + ' / ' + live);
  chk('죽었다는 말이 안 뜬다', !/찾지 못했습니다/.test(r.text));

  /* ── ③-2 망이 미끄러졌을 때 — **살아 있는 링크를 죽었다고 하면 안 된다** ──
     없는 회차를 붙잡아 세우기 시작한 뒤로, 회차 목록을 못 받은 것과 회차가
     없는 것을 구분하지 않으면 그 말이 곧 «네 링크 죽었다» 는 단언이 된다.
     학생은 시험을 못 보고 선생님은 왜 안 왔는지 모른다. */
  console.log('\n── student-finals.json 이 안 올 때 ──');
  let blocked = true;
  await ctx.route('**/student-finals.json', r => blocked ? r.abort() : r.continue());
  r = await open('?exam=' + live);
  chk('죽었다고 말하지 않는다', !/찾지 못했습니다|내려갔습니다/.test(r.text),
    r.text.replace(/\s+/g, ' ').slice(0, 70));
  chk('불러오는 중이라고 말한다', /불러오는 중/.test(r.text));
  chk('링크는 살아 있다고 알려 준다', r.text.indexOf(live) >= 0);
  /* 망이 돌아오면 학생이 아무것도 안 해도 그 시험이 열려야 한다. */
  blocked = false;
  await p.waitForFunction(() => !!document.getElementById('nm'), null, { timeout: 30000 })
    .then(() => chk('망이 돌아오면 저절로 열린다', true))
    .catch(() => chk('망이 돌아오면 저절로 열린다', false, '30초 안에 안 열렸다'));
  const backCur = await p.evaluate(() => (typeof cur !== 'undefined' && cur) ? cur.id : null);
  chk('열린 것이 그 학생 회차다', backCur === live, backCur + ' / ' + live);
  await ctx.unroute('**/student-finals.json');

  /* ── ④ 회차 없이 들어오면 임시 저장 복원은 그대로 산다 ── */
  console.log('\n── 회차 없이 들어온다 (임시 저장 복원) ──');
  r = await open('');
  chk('쓰다 만 회차가 되살아난다', r.cur === live, r.cur || '없음');

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n없어진 회차는 없어졌다고 말하고, 살아 있는 회차는 예전 그대로 열린다.');
  process.exit(fail ? 1 : 0);
})();
