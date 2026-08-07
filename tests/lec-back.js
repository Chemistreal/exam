/* ============================================================
   강의를 보고 나면 **왔던 자리로** 돌아가는가 (브라우저 필요)
   ------------------------------------------------------------
   학생이 개념강의를 여는 길은 하나다 — 자기 성적표(`final.html#r=…`)의
   '오답 개념 클리닉'. 그런데 강의 페이지의 돌아가는 단추는 `final.html` 로
   박혀 있었다. 그래서 이렇게 됐다.

       성적표 → 개념강의 → '파이널로' → **시험 목록**
                                        → 코드를 모르니 잠금 화면에 갇힌다

   학생은 자기 성적표로 돌아가려 했을 뿐인데 갈 수가 없다. 주소를 손으로 칠
   수도 없다(성적표 주소에는 답안이 통째로 실려 있다).

   여기서 지키는 것:
   - 성적표에서 강의로 나가는 링크에 **돌아올 자리가 실린다**(?from=)
   - 그 강의에서 돌아가는 단추가 **성적표를 가리킨다**('‹ 성적표로')
   - 목록에서 연 강의는 예전 그대로 목록으로 간다(선생님 쪽 흐름을 안 바꾼다)
   - **남이 심어 둔 주소로는 안 나간다** — 같은 곳의 성적표만 받는다
   - 시험 목록은 여전히 코드를 묻는다(0000) · 성적표는 안 묻는다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/lec-back.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(180);
const seal = require('./_seal.js');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}/`;
/* 답안이 전부 0(= 다 틀림)이라 오답 개념 클리닉이 반드시 뜬다 —
   강의 링크가 없으면 검사할 것이 없다. */
const REPORT = 'final.html#r=jmchc-6.0';

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
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
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));

  console.log('── 성적표에서 강의로 ──');
  await page.goto(BASE + REPORT, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  chk('성적표는 코드를 묻지 않는다',
    await page.evaluate(() => !!document.getElementById('gate')), false);

  /* 클릭을 가로채 주소만 본다 — 새 탭을 진짜로 열 필요가 없다. */
  const link = await page.evaluate(() => {
    const a = [...document.querySelectorAll('a[href^="lec-"]')][0];
    if (!a) return null;
    const before = a.getAttribute('href');
    a.addEventListener('click', e => e.preventDefault(), { once: true });
    a.click();
    return { before: before, after: a.getAttribute('href'), hash: location.hash };
  });
  chk('성적표에 개념강의 링크가 있다', !!link, true);
  if (!link) { console.log('\nFAIL 1건'); await browser.close(); process.exit(1); }
  chk('돌아올 자리가 실렸다', /\?from=/.test(link.after), true);
  chk('실린 것이 이 성적표다',
    decodeURIComponent((/\?from=([^&]*)/.exec(link.after) || [])[1] || '').indexOf(link.hash) > 0,
    true);
  chk('강의 주소 자체는 그대로다', link.after.split('?')[0], link.before.split('?')[0]);

  console.log('\n── 그 강의에서 돌아가기 ──');
  await page.goto(BASE + link.after, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);
  const back = await page.evaluate(() => {
    const a = document.querySelector('a.back');
    return a ? { href: a.href, text: a.textContent.trim() } : null;
  });
  chk('돌아가는 단추가 있다', !!back, true);
  chk('성적표를 가리킨다', /final\.html#r=/.test(back.href), true);
  chk('성적표라고 적혀 있다', back.text, '‹ 성적표로');

  /* 진짜로 눌러 본다 — 주소만 맞고 화면이 안 뜨면 고친 것이 아니다. */
  await page.click('a.back');
  await page.waitForTimeout(1200);
  chk('눌렀더니 성적표가 떴다',
    await page.evaluate(() => !!document.getElementById('repPDF')), true);
  chk('목록으로 안 갔다',
    await page.evaluate(() => !!document.getElementById('gate')), false);

  console.log('\n── 목록에서 연 강의는 그대로 ──');
  await page.goto(BASE + 'lec-015-electronegativity.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(200);
  const plain = await page.evaluate(() => {
    const a = document.querySelector('a.back');
    return { href: a.getAttribute('href'), text: a.textContent.trim() };
  });
  chk('예전처럼 파이널로 간다', plain.href, 'final.html');
  chk('파이널로라고 적혀 있다', plain.text, '‹ 파이널로');

  console.log('\n── 남이 심어 둔 주소로는 안 나간다 ──');
  const bad = [
    'https://example.com/final.html#r=x',      // 다른 곳
    'final.html',                              // 성적표가 아니다(목록)
    'hub.html#r=x',                            // 다른 화면
    'javascript:alert(1)',                     // 아예 주소가 아니다
  ];
  for (const b of bad) {
    await page.goto(BASE + 'lec-015-electronegativity.html?from=' + encodeURIComponent(b),
                    { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(150);
    chk('안 받는다 · ' + b.slice(0, 28),
      await page.evaluate(() => document.querySelector('a.back').getAttribute('href')),
      'final.html');
  }

  console.log('\n── 시험 목록은 코드를 묻는다 ──');
  const ctx2 = await browser.newContext();          // 열쇠를 안 가진 브라우저
  const p2 = await ctx2.newPage();
  await p2.goto(BASE + 'final.html', { waitUntil: 'networkidle' });
  await p2.waitForTimeout(600);
  chk('목록은 잠겨 있다', await p2.evaluate(() => !!document.getElementById('gate')), true);
  await p2.fill('#gateIn', '0000');
  await p2.click('#gateGo');
  await p2.waitForTimeout(500);
  chk('0000 이면 열린다', await p2.evaluate(() => !!document.getElementById('gate')), false);
  await ctx2.close();

  chk('자바스크립트 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})();
