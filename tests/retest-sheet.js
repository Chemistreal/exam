/* ============================================================
   동형 미니 시험지 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   성적표는 화면에서 보는 것이고, 수업에서는 종이가 필요하다. 틀린 문항의
   동형문제만 뽑아 한 장짜리 시험지로 만든다. 다음 수업 시작할 때 풀리면
   지난 시간 오답이 정말 메워졌는지 그 자리에서 확인된다.

   여기서 지키는 것:
   - 틀린 문항 수만큼 출제된다
   - **화면에서 이미 풀어 본 동형문제는 나오지 않는다.** 답을 아는 문제를 또
     주면 시험지의 뜻이 없다. 그래서 세트의 다른 벌로 바꿔 낸다
   - 아직 회복하지 못한 문항이 앞에 온다
   - 문제지에는 정답이 없고, 정답·해설은 뒤쪽에 따로 모인다(잘라 내면 학생용)
   - 인쇄가 끝나면 화면이 원래대로 돌아온다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/retest-sheet.js
   ============================================================ */
'use strict';
/* 검사가 운영 시트를 읽으면 실 데이터가 심어 둔 데이터를 덮는다.
   실제로 CI 에서 그렇게 깨졌다 — tests/_nosheet.js 의 주석 참고. */
const noSheet = require('./_nosheet.js');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const U = `http://localhost:${PORT}/final.html`;
const EXAM = 'hwol-2018';
const WRONG = [1, 2, 3];

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  /* 브라우저를 깔아 놓고도 조용히 건너뛰면 초록불이 '브라우저 검사까지
     통과했다' 로 읽힌다. 실제로 그랬다 — 통합 셸의 브라우저 검사가 몇 달
     동안 CI 에서 한 번도 안 돌았는데 초록불이었다. 깔아 둔 자리에서는 멈춘다. */
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

(async () => {
  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });
  /* ⚠ 브라우저에 건다 — 화면 하나에 걸면 나중에 여는 화면이 샌다. */
  await noSheet(browser);
  const page = await browser.newPage();
  await page.setViewportSize({ width: 900, height: 1200 });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  // window.print() 는 헤드리스에서 멈춰 있을 수 있으므로 갈아 끼운다
  await page.addInitScript(() => { window.__printed = 0; window.print = () => { window.__printed++; }; });


  await page.goto(U, { waitUntil: 'networkidle' });
  await page.waitForTimeout(700);
  await page.evaluate(([examId, wrong]) => {
    localStorage.clear();
    openExam(examId);
    document.getElementById('nm').value = '시험지';
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      setAns(q, acc[0] || 1);
    }
    wrong.forEach(q => setAns(q, (cur.key[q - 1] % 4) + 1));
    scoreAuto();
  }, [EXAM, WRONG]);
  await page.waitForTimeout(3000);

  // ── 아무것도 안 푼 상태에서 뽑기 ──
  const plain = await page.evaluate(async () => {
    const an = await loadAnalogues(cur.id);
    const items = retestPick(cur, window.__fw || [], an);
    return { n: items.length, qs: items.map(i => i.q), srcs: items.map(i => i.dq._src) };
  });
  chk('틀린 문항 수만큼 출제', plain.n, WRONG.length);
  chk('원문 번호 순서대로', plain.qs, WRONG);
  chk('세트 첫 번째 벌에서 뽑음', plain.srcs, [EXAM, EXAM, EXAM]);

  // ── 1번 동형문제를 화면에서 풀어 본 뒤 다시 뽑기 ──
  const after = await page.evaluate(async () => {
    const ol = document.querySelector('.wb-card[data-q="1"] .wb-opts.is-live');
    const ans = Number(ol.dataset.ans);
    ol.querySelector('li[data-c="' + ans + '"]').click();   // 맞게 푼다 → 회복
    await new Promise(r => setTimeout(r, 200));
    const an = await loadAnalogues(cur.id);
    const items = retestPick(cur, window.__fw || [], an);
    return { qs: items.map(i => i.q), srcs: items.map(i => i.dq._src),
             log: JSON.parse(localStorage.getItem('final:dhlog:' + cur.id) || '[]').length };
  });
  chk('푼 기록이 남음', after.log, 1);
  chk('이미 푼 동형문제 대신 다른 벌로 바꿔 냄', after.srcs[after.qs.indexOf(1)], 'kmchc-2018');
  chk('회복한 문항(1번)은 뒤로 밀림', after.qs[after.qs.length - 1], 1);
  chk('아직 못 푼 문항이 앞에', after.qs.slice(0, 2), [2, 3]);

  // ── 실제 인쇄 문서 ──
  const sheet = await page.evaluate(async () => {
    await printRetest();
    await new Promise(r => setTimeout(r, 400));
    const el = document.getElementById('retestPDF');
    if (!el) return { missing: true };
    return {
      printed: window.__printed,
      bodyClass: document.body.classList.contains('printretest'),
      qs: el.querySelectorAll('.rt-q').length,
      choices: el.querySelectorAll('.rt-ch').length,
      keyRows: el.querySelectorAll('.rt-keyt tbody tr').length,
      sols: el.querySelectorAll('.rt-sol').length,
      // 문제 영역에 정답 표시가 새어 나오지 않아야 한다
      leaked: el.querySelector('.rt-q .is-key, .rt-q [data-ans]') !== null,
      head: (el.querySelector('.rt-m') || {}).textContent || '',
    };
  });
  chk('인쇄가 호출됨', sheet.printed, 1);
  chk('인쇄용 본문만 남기는 클래스', sheet.bodyClass, true);
  chk('문제 3개', sheet.qs, WRONG.length);
  chk('선택지 12개', sheet.choices, WRONG.length * 4);
  chk('정답표 3줄', sheet.keyRows, WRONG.length);
  chk('해설도 실림', sheet.sols > 0, true);
  chk('문제 영역에 정답이 새지 않음', sheet.leaked, false);
  chk('머리글에 이름·문항 수', /시험지/.test(sheet.head) && /3문항/.test(sheet.head), true);

  // ── 인쇄 뒤 정리 ──
  const cleaned = await page.evaluate(() => {
    window.dispatchEvent(new Event('afterprint'));
    return { left: !!document.getElementById('retestPDF'),
             cls: document.body.classList.contains('printretest'),
             reportVisible: !!document.querySelector('.wb-card') };
  });
  chk('인쇄 뒤 임시 문서 제거', cleaned.left, false);
  chk('인쇄 뒤 클래스 해제', cleaned.cls, false);
  chk('성적표 화면은 그대로', cleaned.reportVisible, true);
  chk('JS 오류 없음', errs, []);

  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
