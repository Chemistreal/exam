/* ============================================================
   답을 넣기 **전** 화면에 정답이 없다
   ------------------------------------------------------------
   2026-08-10, 선생님이 알려 주셨다 — 문제지에 정답이 문제 바로 옆에 적혀
   있다. 열어 보니 문제지 PDF 서른아홉 개 가운데 **스물여섯 개**가 그랬다.

     · 열일곱은 뒤에 정답표가 통째로 붙어 있었다
     · 셋(2017·2018·2019)은 아예 문제지가 아니라 **해설편**이었다 —
       크롭 예순 장이 전부 거기서 잘려 나왔다
     · 2017·2018 은 '정답률 : %  ④' 처럼 답 글자가 문제 옆에 인쇄돼 있었다

   그리고 화면 쪽에도 같은 구멍이 있었다. `examAssetsHTML` 은 답안지 바로
   위에 '공식 정답 PDF ↓' · '문제편·해설편 PDF ↓' · '정답 · 문항별 해설 ↓'
   을 같이 걸고 있었다. 답을 넣기 전에 한 번만 누르면 답이 손에 들어왔다.

   여기서 지키는 것.

     · **답 넣는 화면**에는 문제지 PDF 말고 정답·해설 링크가 없다
     · **채점 뒤 성적표**에는 있다 (없애는 게 아니라 자리를 옮긴 것이다)

   파일 쪽은 `tools/pdf_answer_leak.py` 가 본다. 여기서는 화면을 본다.

   실행:  node tests/answer-not-before.js
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

const ANSWERISH = /공식 정답 PDF|문제편·해설편 PDF|정답 · 문항별 해설|정답 · 개념표/;

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

  /* 답지·해설지를 **가진** 회차로 본다. 안 가진 회차로 보면 링크가 없는
     것이 당연해서, 자가 아무것도 안 막아도 초록불이 된다. */
  const withBook = await p.evaluate(() =>
    (FINAL_EXAMS.filter(e => e.answerPdf || e.bookPdf).map(e => e.id)));
  console.log('\n■ 답지·해설지를 가진 회차 ' + withBook.length + '개: ' + withBook.join(', '));
  chk('그런 회차가 있다(없으면 이 검사는 아무것도 안 막는다)', withBook.length > 0, true);

  for (const eid of withBook.slice(0, 2)) {
    const before = await p.evaluate((eid) => {
      openExam(eid);
      return document.getElementById('app').innerText.replace(/\s+/g, ' ');
    }, eid);
    console.log('\n■ ' + eid + ' · 답 넣기 전 화면');
    chk('문제지 PDF 는 있다', /문제지 PDF/.test(before), true);
    chk('정답·해설 링크가 없다', ANSWERISH.test(before), false);

    /* 다 맞게 넣고 채점한 뒤 성적표에는 있어야 한다 — 없애는 게 아니라
       자리를 옮긴 것이다. 여기를 안 보면 "그냥 지워 버렸다" 와 구별이 안 된다. */
    const after = await p.evaluate((eid) => {
      const ex = FINAL_EXAMS.find(e => e.id === eid);
      openExam(eid);
      for (let q = 1; q <= ex.nQ; q++) setAns(q, ex.key[q - 1] || 1);
      document.getElementById('nm').value = '자료링크점검';
      document.getElementById('sch').value = 'X중';
      scoreAuto();
      return new Promise(r => setTimeout(() =>
        r(document.getElementById('app').innerText.replace(/\s+/g, ' ')), 900));
    }, eid);
    console.log('■ ' + eid + ' · 채점 뒤 성적표');
    chk('성적표에는 정답·해설 링크가 있다', ANSWERISH.test(after), true);
  }

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;
  await browser.close();
  console.log(fail ? `\n실패 ${fail}` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})();
