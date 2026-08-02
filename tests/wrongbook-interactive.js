/* ============================================================
   오답노트 동형문제 풀이 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   동형문제가 읽기 전용이면 학생은 눈으로 훑고 정답을 펼쳐 보면 끝난다.
   답을 **고르게** 하면 자기 판단을 한 번 걸고 넘어가고, 틀렸을 때 "왜 하필
   그걸 골랐는지"를 그 자리에서 짚어 줄 수 있다. 2400문항 모두 오답 선택지마다
   그 선택으로 이끄는 오개념 문장(`misconceptions`)을 갖고 있다.

   그리고 이게 있어야 처음으로 **"그래서 고쳤나"** 를 잴 수 있다. 원문을 틀린
   문항의 동형문제를 맞히면 회복이다.

   여기서 지키는 것:
   - 처음엔 정답도 판정도 보이지 않는다(색칠된 보기가 먼저 보이면 뜻이 없다)
   - 고르면 즉시 맞고 틀림이 뜨고, 틀리면 그 선택지의 오개념이 나온다
   - 한 번 고르면 바꿀 수 없다(눌러 보며 정답 찾기는 푸는 것이 아니다)
   - 고른 뒤 해설이 자동으로 펼쳐진다
   - 성취가 기록되고 회복률 섹션이 그 자리에서 갱신된다
   - 새로고침해도 기록이 남는다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/wrongbook-interactive.js
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


  await page.goto(U, { waitUntil: 'networkidle' });
  await page.waitForTimeout(700);
  await page.evaluate(([examId, wrong]) => {
    localStorage.clear();
    openExam(examId);
    document.getElementById('nm').value = '클릭이';
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      setAns(q, acc[0] || 1);
    }
    wrong.forEach(q => setAns(q, (cur.key[q - 1] % 4) + 1));
    scoreAuto();
  }, [EXAM, WRONG]);
  await page.waitForTimeout(3000);

  const before = await page.evaluate(() => ({
    live: document.querySelectorAll('.wb-card .wb-opts.is-live').length,
    verdicts: [].slice.call(document.querySelectorAll('.wb-verdict')).filter(v => !v.hidden).length,
    keyed: document.querySelectorAll('.wb-opts li.is-key').length,
    recovery: (document.getElementById('recovery') || {}).innerHTML || '',
  }));
  chk('오답 3문항 × 동형 2벌 = 보기 6묶음', before.live, WRONG.length * 2);
  chk('처음엔 판정이 안 보임', before.verdicts, 0);
  chk('처음엔 정답 표시 없음', before.keyed, 0);
  chk('처음엔 회복률 섹션 없음', before.recovery, '');

  // 맞게 고른다
  const right = await page.evaluate(() => {
    const ol = document.querySelector('.wb-card .wb-opts.is-live');
    ol.querySelector('li[data-c="' + Number(ol.dataset.ans) + '"]').click();
    const dh = ol.closest('.wb-dh');
    return { verdict: dh.querySelector('.wb-verdict').textContent.trim(),
             marked: !!dh.querySelector('li.is-ok'),
             opened: dh.querySelector('details.wb-dh-reveal').open,
             stillLive: ol.classList.contains('is-live') };
  });
  chk('맞으면 맞았다고 알려 준다', /맞았습니다/.test(right.verdict), true);
  chk('고른 보기에 표시', right.marked, true);
  chk('해설이 자동으로 펼쳐짐', right.opened, true);
  chk('다 푼 보기는 더 이상 눌리지 않음', right.stillLive, false);

  // 오개념이 달린 오답으로 고른다
  const wrongPick = await page.evaluate(() => {
    const ols = [].slice.call(document.querySelectorAll('.wb-card .wb-opts.is-live'));
    const ol = ols.find(o => [].slice.call(o.children)
      .some(li => Number(li.dataset.c) !== Number(o.dataset.ans) && li.dataset.mis));
    const ans = Number(ol.dataset.ans);
    const bad = [].slice.call(ol.children).find(li => Number(li.dataset.c) !== ans && li.dataset.mis);
    const expected = bad.dataset.mis;
    bad.click();
    const dh = ol.closest('.wb-dh');
    return { verdict: dh.querySelector('.wb-verdict').textContent.trim(),
             why: (dh.querySelector('.wb-verdict-why') || {}).textContent || '',
             expected: expected,
             marked: !!dh.querySelector('li.is-no'),
             keyShown: !!dh.querySelector('li.is-key') };
  });
  chk('틀리면 틀렸다고 알려 준다', /틀렸습니다/.test(wrongPick.verdict), true);
  chk('고른 오답에 표시', wrongPick.marked, true);
  chk('정답도 함께 보여 준다', wrongPick.keyShown, true);
  chk('그 선택지의 오개념을 그대로 보여 준다',
    wrongPick.why.includes(wrongPick.expected.slice(0, 30)), true);

  await page.waitForTimeout(300);
  const rec = await page.evaluate(examId => ({
    shown: !!(document.getElementById('recovery') || {}).innerHTML.trim(),
    text: (document.getElementById('recovery') || {}).textContent.replace(/\s+/g, ' '),
    logged: JSON.parse(localStorage.getItem('final:dhlog:' + examId) || '[]').length,
  }), EXAM);
  chk('회복률 섹션이 그 자리에서 생김', rec.shown, true);
  chk('회복한 문항을 말해 준다', /회복한 문항/.test(rec.text), true);
  chk('시도 2건이 기록됨', rec.logged, 2);

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  chk('새로고침해도 기록이 남는다',
    await page.evaluate(examId => JSON.parse(localStorage.getItem('final:dhlog:' + examId) || '[]').length, EXAM), 2);

  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
