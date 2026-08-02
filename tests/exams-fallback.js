/* ============================================================
   exams.json 이 없을 때도 앱이 도는가 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   시험 목록을 exams.json 한 곳으로 뺐더니, **그 파일 하나가 늦게 오면 앱 전체가
   죽는** 문제가 생겼다. 실제로 배포 직후 CDN 전파 시차 때문에 성적표 링크로
   들어온 학생이 "시험 목록을 불러오지 못했습니다 · HTTP 404" 만 보고 끝났다.
   분리하기 전에는 final.html 이 자체 완결이라 없던 문제다.

   이제 세 겹으로 받는다.
     1) exams.json (짧게 두 번까지 다시 시도)
     2) 서비스워커가 캐시해 둔 것
     3) 파일에 심어 둔 예비본 FALLBACK_EXAMS

   예비본은 손으로 관리하는 사본이 아니다. tools/gen_exam_fallback.py 가
   exams.json 에서 심고 CI 가 매번 대조한다.

   여기서 지키는 것:
   - exams.json 이 404 여도 성적표가 정상으로 뜬다(오류 화면이 아니라)
   - 채점·오답노트·동형문제가 그대로 돈다
   - 공유 링크(#r=)도 열린다 — 학생이 실제로 막혔던 그 경로다
   - 예비본 내용이 exams.json 과 같다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/exams-fallback.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}`;

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

const EXAMS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'exams.json'), 'utf8'));

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* exams.json 만 404 로 만들고 나머지는 그대로 통과시킨다 */
async function blockExams(page) {
  await page.route('**/exams.json', route => route.fulfill({ status: 404, body: 'not found' }));
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });

  // ── 1. 시험 목록 화면 ──
  {
    const page = await browser.newPage();
    const errs = []; page.on('pageerror', e => errs.push(e.message));
    await blockExams(page);
    await page.goto(`${BASE}/final.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);   // 재시도 600ms + 여유
    const r = await page.evaluate(() => ({
      n: (typeof FINAL_EXAMS !== 'undefined') ? FINAL_EXAMS.length : -1,
      cards: document.querySelectorAll('.card').length,
      errorShown: /시험 목록을 불러오는 중/.test(document.body.innerText),
    }));
    chk('exams.json 404 여도 시험 목록이 뜬다', r.n, EXAMS.length);
    chk('카드가 모두 그려진다', r.cards, EXAMS.length);
    chk('오류 화면이 아니다', r.errorShown, false);
    chk('JS 오류 없음', errs, []);
    await page.close();
  }

  // ── 2. 채점 · 오답노트 · 동형문제 ──
  {
    const page = await browser.newPage();
    const errs = []; page.on('pageerror', e => errs.push(e.message));
    await blockExams(page);
    await page.goto(`${BASE}/final.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    const r = await page.evaluate(async () => {
      openExam('hwol-2018');
      document.getElementById('nm').value = '예비본';
      for (let q = 1; q <= cur.nQ; q++) {
        const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
        setAns(q, acc[0] || 1);
      }
      [1, 2, 3].forEach(q => setAns(q, (cur.key[q - 1] % 4) + 1));
      scoreAuto();
      await new Promise(r => setTimeout(r, 3000));
      const cards = document.querySelectorAll('.wb-card');
      return { cards: cards.length,
               dh: [].slice.call(cards).map(c => c.querySelectorAll('.wb-dh').length),
               live: document.querySelectorAll('.wb-opts.is-live').length };
    });
    chk('채점되어 오답 카드 3장', r.cards, 3);
    chk('동형문제 2벌씩 그대로', r.dh, [2, 2, 2]);
    chk('눌러 풀기도 그대로', r.live, 6);
    chk('JS 오류 없음', errs, []);
    await page.close();
  }

  // ── 3. 공유 링크 — 학생이 실제로 막혔던 경로 ──
  {
    const page = await browser.newPage();
    const errs = []; page.on('pageerror', e => errs.push(e.message));
    await blockExams(page);
    // 먼저 정상 페이지에서 링크를 만든 뒤, 그 해시로 다시 들어간다
    const link = await (async () => {
      const p2 = await browser.newPage();
      await p2.goto(`${BASE}/final.html`, { waitUntil: 'networkidle' });
      await p2.waitForTimeout(700);
      const l = await p2.evaluate(() => {
        const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-4'), sel2 = {};
        for (let q = 1; q <= ex.nQ; q++) sel2[q] = ex.key[q - 1];
        sel2[5] = (ex.key[4] % 4) + 1;
        return shareLinkFinal(ex, sel2, '오승민', '');
      });
      await p2.close();
      return l;
    })();
    await page.goto(link, { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    const r = await page.evaluate(() => ({
      name: (window.__rpt || {}).name || '',
      cards: document.querySelectorAll('.wb-card').length,
      errorShown: /시험 목록을 불러오는 중/.test(document.body.innerText),
    }));
    chk('exams.json 404 여도 공유 링크가 열린다', r.errorShown, false);
    chk('이름이 복원된다', r.name, '오승민');
    chk('오답 카드도 그려진다', r.cards > 0, true);
    chk('JS 오류 없음', errs, []);
    await page.close();
  }

  // ── 4. 학생 제출 페이지 ──
  {
    const page = await browser.newPage();
    const errs = []; page.on('pageerror', e => errs.push(e.message));
    await blockExams(page);
    await page.goto(`${BASE}/final-submit.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    const r = await page.evaluate(() => ({
      n: (typeof FINAL_EXAMS !== 'undefined') ? FINAL_EXAMS.length : -1,
      btns: document.querySelectorAll('.exbtn').length,
    }));
    chk('제출 페이지도 예비본으로 뜬다', r.n, EXAMS.length);
    chk('시험 버튼이 모두 그려진다', r.btns, EXAMS.length);
    chk('JS 오류 없음', errs, []);
    await page.close();
  }

  // ── 5. 예비본이 exams.json 과 같은 내용인가 ──
  {
    const page = await browser.newPage();
    await blockExams(page);
    await page.goto(`${BASE}/final.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    const same = await page.evaluate(want => JSON.stringify(FINAL_EXAMS) === JSON.stringify(want), EXAMS);
    chk('예비본 내용이 exams.json 과 완전히 같다', same, true);
    await page.close();
  }

  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
