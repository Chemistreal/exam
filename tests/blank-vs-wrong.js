/* ============================================================
   무응답과 오답은 다른 일이다 — 성적표가 그렇게 말하는가
   ------------------------------------------------------------
   화올·KMChC 기출과 기출동형은 **오답 −1** 로 채점한다. 그 회차에서

       비우면        0점
       찍고 틀리면  −1점

   이다. 그런데 성적표는 둘을 '틀린 문항' 하나로 묶어 보여 주고 있었다
   (2026-08-10 에 선생님이 짚으셨다). 학생은 자기가 점수를 **흘린 것**인지
   **내준 것**인지 알 수 없었다. 채점은 이미 갈라 세고 있었는데
   (`finalRawScore` 가 `w.a>=1&&w.a<=4` 만 오답으로 센다) 화면만 묶고 있었다.

   여기서 지키는 것.

     · 감점이 있는 회차는 화면이 '오답' 과 '무응답' 을 따로 적는다
     · 그 수가 실제 답안과 맞는다
     · 원점수 = 맞은 개수×3 − 오답×1 (무응답은 안 깎는다)
     · **무감점 회차(JMChC·산과염기)는 갈라 적지 않는다** — 거기서는 비우나
       찍고 틀리나 0점이라 나눌 뜻이 없다. 없는 구분을 만들면 말이 는다

   실행:  node tests/blank-vs-wrong.js
     (정적 서버가 8931 포트에 떠 있어야 한다)
   ============================================================ */
'use strict';
const noSheet = require('./_nosheet.js');
require('./_watchdog.js')(120);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const PORT = Number(process.env.PORT || 8931);

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  /* ⚠ **시트를 막고 시작한다.** 안 막으면 검사가 학원의 진짜 시트를 읽고,
     채점하는 검사는 **거기에 줄을 쓴다.** 2026-08-12 에 실제로 그랬다 —
     이 검사가 판을 돌 때마다 «무응답점검·분류점검·자료링크점검» 같은 이름이
     선생님 시트에 쌓이고 있었다(POST 를 세어서 확인했다).
     `tests/_nosheet.js` 머리말이 처음부터 이르던 일이다. */
  await noSheet(browser);
  const p = await browser.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 30000 });

  /* 한 회차를 정해진 대로 채운다 — 맞게 / 찍고 틀리게 / 비우고.
     전항정답(multi)·폐기(voided) 문항은 어떤 답을 넣어도 맞으므로 건드리지
     않는다. 여기 넣으면 '틀리게 넣었는데 맞았다' 가 되어 수가 안 맞는다. */
  const run = (eid, nWrong, nBlank) => p.evaluate(([eid, nWrong, nBlank]) => {
    const ex = FINAL_EXAMS.find(e => e.id === eid);
    openExam(eid);
    const allc0 = q => (ex.miss || []).indexOf(q) >= 0 || (ex.voided || []).indexOf(+q) >= 0
      || ((ex.multi || {})[String(q)] || []).length >= 4 || !(ex.key[q - 1] >= 1 && ex.key[q - 1] <= 4);
    let w = 0, b = 0, c = 0;
    for (let q = 1; q <= ex.nQ; q++) {
      const k = ex.key[q - 1];
      if (!allc0(q) && w < nWrong) { setAns(q, (k % 4) + 1); w++; }
      else if (!allc0(q) && b < nBlank) { setAns(q, 0); b++; }
      else { setAns(q, k); c++; }
    }
    document.getElementById('nm').value = '무응답점검';
    document.getElementById('sch').value = 'X중';
    scoreAuto();
    return new Promise(r => setTimeout(() => {
      const t = document.getElementById('app').innerText.replace(/\s+/g, ' ');
      r({ text: t, nQ: ex.nQ, wrong: w, blank: b, pen: finalPenalty(ex),
          correct: ex.nQ - w - b });
    }, 900));
  }, [eid, nWrong, nBlank]);

  // ── 감점이 있는 회차 ────────────────────────────────────────────
  const a = await run('hwol-2018', 7, 5);
  console.log(`\n■ hwol-2018 (오답 −${a.pen}) · 맞음 ${a.correct} · 오답 ${a.wrong} · 무응답 ${a.blank}`);
  chk('감점 회차다', a.pen, 1);
  chk('오답 수를 따로 적는다', new RegExp('' + a.wrong + '개 오답').test(a.text), true);
  chk('무응답 수를 따로 적는다', new RegExp('' + a.blank + '개 무응답').test(a.text), true);
  chk('두 수가 다르다(같으면 못 가른 것과 구별이 안 된다)', a.wrong !== a.blank, true);
  // 원점수 = 맞은 개수×3 − 오답×1. 무응답은 안 깎는다.
  const want = a.correct * 3 - a.wrong * a.pen;
  chk('원점수가 무응답을 안 깎는다', new RegExp(want + '/' + a.nQ * 3).test(a.text), true);
  chk('무응답까지 깎은 값은 안 나온다',
    new RegExp((a.correct * 3 - (a.wrong + a.blank) * a.pen) + '/' + a.nQ * 3).test(a.text), false);

  // ── 무감점 회차 ────────────────────────────────────────────────
  const b = await run('jmchc-1', 7, 5);
  console.log(`\n■ jmchc-1 (무감점) · 맞음 ${b.correct} · 안 맞힘 ${b.wrong + b.blank}`);
  chk('무감점 회차다', b.pen, 0);
  chk('무감점 회차는 갈라 적지 않는다', /개 무응답 · 0점/.test(b.text), false);
  chk('원점수는 맞은 개수×3', new RegExp((b.correct * 3) + '/' + b.nQ * 3).test(b.text), true);

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;
  await browser.close();
  console.log(fail ? `\n실패 ${fail}` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})();
