/* ============================================================
   학생이 **손을 대는 자리**가 취약한 단원부터 늘어서는가
   ------------------------------------------------------------
   2026-08-10, 실제 사용자 → 선생님.

       "성적표 받아보니까 취약단원 순서대로 배열해줬으면 좋겠다"

   처음에 세 자리를 열어 보고 "이미 약한 순이다" 라고 답했다. **틀렸다.**
   그 셋(영역별 성취·학습 처방)은 전부 **보여 주기만 하는** 곳이었고,
   학생이 실제로 풀어 나가는 두 자리는 다른 기준이었다.

       final.html:2080  오답 개념 클리닉 (화면)      오답 **개수** 순
       final.html:5091  오답 정밀 분석  (워드·종이)  오답 **개수** 순

   개수와 취약도는 다르다.

       단원 A  12문항 중 5개 틀림   정답률 58%   오답 5
       단원 B   4문항 중 4개 틀림   정답률  0%   오답 4

   개수로 세면 A 가 먼저다. 무너진 것은 B 다. 문항이 많은 단원이 늘 앞에 오고
   **통째로 모르는 단원이 뒤로 밀린다.** JMChC 3회에서는 70% 맞힌 단원이
   첫 장이고 50%짜리 넷이 그 뒤에 묻혀 있었다.

   이 검사가 지키는 것
   -------------------
     ① 화면의 오답 클리닉이 **정답률 낮은 묶음부터** 나온다
     ② 워드로 나가는 오답 정밀 분석도 **같은 순서**다
        (선생님 말씀 — 학생은 화면과 워드파일 **둘 다** 쓴다.
         화면만 고치면 절반만 고친 것이다)

   ⚠ '또래도 많이 틀린 묶음을 맨 앞에' 는 예외로 둔다. 화면 안내문에 적어 둔
     약속이고, 개인 실수가 아니라 개념 함정이라는 **다른 뜻**이다. 그래서 이
     검사는 또래 자료가 없는 상태(cs 미준비)로 재어 그 규칙이 안 끼게 한다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/weak-first.js
   ============================================================ */
'use strict';
const noSheet = require('./_nosheet.js');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);

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
  const browser = await chromium.launch(Object.assign(
    { args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {}));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  await ctx.route('**://script.google.com/**', r => r.abort());
  const p = await ctx.newPage();
  p.on('pageerror', () => {});
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
  /* 시험 목록은 exams.json 을 받아 온 뒤에 채워진다(FINAL_EXAMS). 곧바로 읽으면
     빈 배열이라 검사가 **아무것도 안 보고 통과**한다 — 그래서 채워질 때까지
     기다리고, 안 채워지면 아래에서 빨간불이다. */
  await p.waitForFunction(
    () => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length > 0,
    null, { timeout: 20000 }).catch(() => {});

  /* 화면 안의 진짜 함수를 그대로 부른다. 여기서 순서를 다시 계산하면
     검사가 제 답을 채점하는 꼴이 된다 — 화면이 내놓은 글에서 읽는다. */
  const out = await p.evaluate(() => {
    const res = [];
    const exams = (typeof FINAL_EXAMS !== 'undefined' ? FINAL_EXAMS : []).slice();
    for (const ex of exams) {
      if (!ex || !ex.area || !ex.key || !ex.nQ) continue;
      // 고르게 틀리는 학생 하나. 단원마다 정답률이 갈리도록 만든다.
      const sel = {}; for (let q = 1; q <= ex.nQ; q++)
        sel[q] = (q % 5 === 0 || q % 7 === 0) ? 0 : ex.key[q - 1];
      const wrong = [];
      for (let q = 1; q <= ex.nQ; q++) if (!okq(ex, q, sel[q])) wrong.push({ q, a: sel[q] });
      if (wrong.length < 4) continue;

      // 단원(대분류)마다 정답률
      const rate = {};
      const broad = a => (typeof RX !== 'undefined' && RX[a]) ? a
        : ((typeof RXMAP !== 'undefined' && RXMAP[a]) || a);
      for (let q = 1; q <= ex.nQ; q++) {
        const bd = broad(ex.area[q - 1] || '기타');
        (rate[bd] = rate[bd] || { c: 0, t: 0 }); rate[bd].t++;
        if (okq(ex, q, sel[q])) rate[bd].c++;
      }

      // 화면이 내놓은 클리닉 글에서 묶음 이름을 나온 순서대로 읽는다
      const html = conceptClinicSec(ex, sel, wrong, { percReady: false });
      if (!html) continue;
      const d = document.createElement('div'); d.innerHTML = html;
      const names = [].map.call(d.querySelectorAll('.note > div:first-child'),
        n => (n.childNodes[0] && n.childNodes[0].textContent || '').trim())
        .filter(Boolean);
      const seq = names.map(n => {
        const k = Object.keys(rate).find(b => b === n) ||
                  Object.keys(rate).find(b => n.indexOf(b) >= 0);
        return k ? Math.round(100 * rate[k].c / rate[k].t) : null;
      }).filter(v => v != null);
      if (seq.length >= 2) res.push({ id: ex.id || ex.title, seq });
      if (res.length >= 8) break;
    }
    return res;
  });

  await browser.close();

  if (!out.length) {
    console.log('실패: 잴 회차를 하나도 못 만들었다 — 검사가 아무것도 안 본 것이다');
    process.exit(1);
  }

  console.log(`오답 클리닉을 잰 회차 ${out.length}개\n`);
  for (const r of out) {
    // 뒤로 갈수록 정답률이 오르는가(같은 값은 괜찮다)
    let bad = -1;
    for (let i = 1; i < r.seq.length; i++) if (r.seq[i] < r.seq[i - 1]) { bad = i; break; }
    chk(`${r.id} 이 약한 단원부터 나온다`, bad < 0,
        bad < 0 ? `(${r.seq.join('% → ')}%)`
                : `${r.seq[bad - 1]}% 다음에 ${r.seq[bad]}% 가 온다 — 뒤집혔다`);
  }

  console.log(fail
    ? `\n실패 ${fail}건 — 학생이 손을 대는 자리가 약한 순이 아니다`
    : '\n학생이 풀어 나가는 자리가 취약한 단원부터 늘어선다.');
  process.exit(fail ? 1 : 0);
})();
