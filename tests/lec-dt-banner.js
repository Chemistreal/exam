/* ============================================================
   DT 성적표에서 연 강의는 DT 의 말로 시작하는가 (브라우저 필요)
   ------------------------------------------------------------
   강의 128장은 두 곳에서 열린다 — 파이널 진단 성적표(final.html), 그리고
   DT 주간 성적표(새 탭). 강의 맨 위는 파이널 쪽 말뿐이라 DT 학생에게는
   «‹ 파이널로»(누르면 시험 목록 · 잠금 화면)와 «이번 진단에서 …» 가 보였다.

   DT 는 주소에 `?from=dt&c=<ch1|ch2|gc>&r=<1–99>` 를 싣고 #절 을 붙인다.
   (`tools/lec_dt_banner.py` 머리말)

   여기서 지키는 것:
   - from=dt 이면 맨 위에 «DT 화학Ⅱ 5회에서 틀린 개념입니다 · 성적표로 돌아가기»
   - 파이널로 가는 단추와 «이번 진단에서 …» 문장이 걷힌다
   - #s03 으로 열면 여전히 03절이 화면 맨 위에 온다(한 줄이 가리지 않는다)
   - 인쇄에는 한 줄이 안 찍힌다
   - 표시가 없으면 예전 그대로다
   - c·r 가 어긋나면 «DT 성적표에서 틀린 개념입니다» — 주소의 글자는 화면에 안 옮긴다
   - «성적표로 돌아가기» 는 탭을 닫고, 못 닫으면 뒤로 / DT 성적표로 간다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/lec-dt-banner.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(180);
const seal = require('./_seal.js');
const noSheet = require('./_nosheet.js');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}/`;
const LEC = 'lec-078-lechatelier-pressure.html';
const DT = 'https://chemistreal.github.io/DT/report.html';

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

/* 화면에서 읽어 올 것 — 한 줄 · 파이널 단추 · 첫 칸 · 03절 자리 */
const look = () => {
  const b = document.querySelector('.dtb');
  const back = document.querySelector('a.back');
  const hw = document.querySelector('main .hw');
  const s3 = document.getElementById('s03');
  return {
    banner: b ? b.textContent.replace(/\s+/g, ' ').trim() : null,
    title: b ? b.querySelector('.dtb__t').textContent : null,
    tags: b ? [...b.querySelectorAll('*')].map(e => e.tagName.toLowerCase()) : null,
    goHref: b ? b.querySelector('a').href : null,
    firstInMain: b ? b === document.querySelector('main').firstElementChild : null,
    pos: b ? getComputedStyle(b).position : null,
    backShown: !!(back && back.offsetParent),
    backText: back ? back.textContent.trim() : null,
    backHref: back ? back.getAttribute('href') : null,
    hwShown: !!(hw && hw.offsetParent),
    hw: hw ? hw.textContent.trim().slice(0, 30) : null,
    s3top: s3 ? Math.round(s3.getBoundingClientRect().top) : null,
    scripts: document.querySelectorAll('script').length,
  };
};

(async () => {
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  await noSheet(browser);
  const errs = [];
  const dialogs = [];
  const open = async (ctx) => {
    const p = await (ctx || browser).newPage();
    p.on('pageerror', e => errs.push(e.message));
    p.on('dialog', d => { dialogs.push(d.message()); d.dismiss().catch(() => {}); });
    return p;
  };
  /* DT 성적표는 밖에 있다 — 나가지 않고 이 자리에서 대신 답한다. */
  const stubDT = async (ctx) => {
    await ctx.route(DT + '*', r => r.fulfill({
      contentType: 'text/html; charset=utf-8',
      body: '<!doctype html><meta charset="utf-8"><title>DT</title><p id="dt">DT report</p>' +
            '<a id="go" target="_blank" rel="noopener" href="' + BASE + LEC +
            '?from=dt&c=ch2&r=5#s03">078</a>',
    }));
  };

  console.log('── DT 에서 연 강의 (?from=dt&c=ch2&r=5#s03) ──');
  const page = await open();
  await page.goto(BASE + LEC + '?from=dt&c=ch2&r=5#s03', { waitUntil: 'load' });
  await page.waitForFunction(() => document.readyState === 'complete');
  let v = await page.evaluate(look);
  chk('한 줄이 뜬다', v.banner, 'DT 화학Ⅱ 5회에서 틀린 개념입니다 · 성적표로 돌아가기');
  chk('앞말이 정해 둔 대로다', v.title, 'DT 화학Ⅱ 5회에서 틀린 개념입니다');
  chk('돌아가기는 DT 성적표(학생 코드 없음)', v.goHref, DT);
  chk('main 의 맨 앞에 앉는다', v.firstInMain, true);
  chk('떠 있지 않다(문서 흐름)', v.pos, 'static');
  chk('파이널로 단추가 안 보인다', v.backShown, false);
  chk('첫 칸에서 «이번 진단에서» 가 걷혔다', /이번 진단/.test(v.hw), false);
  chk('첫 칸의 나머지는 남는다', v.hw.startsWith('이 1강을 끝까지'), true);
  chk('03절이 화면 맨 위에 온다 (0–40px)', v.s3top >= 0 && v.s3top <= 40, true);
  await page.evaluate(() => window.scrollTo(0, 0));
  chk('맨 위로 올리면 한 줄이 보인다',
    await page.evaluate(() => { const r = document.querySelector('.dtb').getBoundingClientRect();
      return r.top >= 0 && r.bottom <= innerHeight && r.height > 0; }), true);
  await page.emulateMedia({ media: 'print' });
  chk('인쇄에는 안 찍힌다',
    await page.evaluate(() => getComputedStyle(document.querySelector('.dtb')).display), 'none');
  await page.emulateMedia({ media: 'screen' });

  for (const [q, want] of [
    ['c=ch1&r=12', 'DT 화학Ⅰ 12회에서 틀린 개념입니다'],
    ['c=gc&r=1', 'DT 일반화학 1회에서 틀린 개념입니다'],
    ['c=ch2&r=99', 'DT 화학Ⅱ 99회에서 틀린 개념입니다'],
  ]) {
    await page.goto(BASE + LEC + '?from=dt&' + q, { waitUntil: 'domcontentloaded' });
    chk('과목·회차 · ' + q, await page.evaluate(() => document.querySelector('.dtb__t').textContent), want);
  }

  console.log('\n── 표시 없이 연 강의는 그대로 ──');
  await page.goto(BASE + LEC, { waitUntil: 'load' });
  await page.waitForFunction(() => document.readyState === 'complete');
  v = await page.evaluate(look);
  chk('한 줄이 없다', v.banner, null);
  chk('파이널로 단추가 보인다', v.backShown, true);
  chk('파이널로라고 적혀 있다', [v.backText, v.backHref], ['‹ 파이널로', 'final.html']);
  chk('첫 칸이 그대로다', v.hw.startsWith('이번 진단에서'), true);
  chk('첫 칸이 보인다', v.hwShown, true);
  await page.goto(BASE + LEC + '#s03', { waitUntil: 'load' });
  await page.waitForFunction(() => document.readyState === 'complete');
  v = await page.evaluate(look);
  chk('#s03 도 그대로 맨 위', v.s3top >= 0 && v.s3top <= 40, true);
  /* 성적표(final.html)에서 온 ?from= 은 여전히 lec_back 이 받는다 */
  await page.goto(BASE + LEC + '?from=' + encodeURIComponent('final.html#r=jmchc-6.0'),
                  { waitUntil: 'domcontentloaded' });
  v = await page.evaluate(look);
  chk('파이널 성적표에서 오면 한 줄 없이 ‹ 성적표로', [v.banner, v.backText], [null, '‹ 성적표로']);

  console.log('\n── 어긋난 표시 · 심어 둔 글자 ──');
  const before = (await page.evaluate(look)).scripts;
  const bad = [
    'c=%3Cscript%3Ealert(1)%3C%2Fscript%3E&r=5',
    'c=ch2&r=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E',
    'c=ch2', 'r=5', '', 'c=CH2&r=5', 'c=ch3&r=5', 'c=__proto__&r=5', 'c=toString&r=5',
    'c=ch2&r=0', 'c=ch2&r=100', 'c=ch2&r=05', 'c=ch2&r=5.5', 'c=ch2&r=-5', 'c=ch2&r=5%0A',
  ];
  for (const q of bad) {
    await page.goto(BASE + LEC + '?from=dt' + (q ? '&' + q : '') + '#s03', { waitUntil: 'load' });
    await page.waitForFunction(() => document.readyState === 'complete');
    v = await page.evaluate(look);
    chk('두루뭉술한 한 줄 · ' + (q || '(c·r 없음)').slice(0, 40),
      [v.title, v.tags, v.backShown, v.scripts],
      ['DT 성적표에서 틀린 개념입니다', ['span', 'span', 'a'], false, before]);
  }
  chk('경고창이 한 번도 안 떴다', dialogs, []);
  for (const q of ['from=DT&c=ch2&r=5', 'from=dtx&c=ch2&r=5', 'c=ch2&r=5']) {
    await page.goto(BASE + LEC + '?' + q, { waitUntil: 'domcontentloaded' });
    v = await page.evaluate(look);
    chk('from=dt 가 아니면 예전 그대로 · ' + q, [v.banner, v.backShown], [null, true]);
  }

  console.log('\n── 성적표로 돌아가기 ──');
  /* 1) 진짜 길: DT 성적표에서 새 탭(noopener)으로 열고 → 누르면 탭이 닫힌다 */
  const ctx1 = await browser.newContext();
  await stubDT(ctx1);
  const dtPage = await open(ctx1);
  await dtPage.goto(DT, { waitUntil: 'load' });
  const [tab] = await Promise.all([ctx1.waitForEvent('page'), dtPage.click('#go')]);
  tab.on('pageerror', e => errs.push(e.message));
  await tab.waitForLoadState('load');
  await tab.waitForFunction(() => document.readyState === 'complete');
  chk('새 탭에도 한 줄이 뜬다', await tab.evaluate(() => document.querySelector('.dtb__t').textContent),
    'DT 화학Ⅱ 5회에서 틀린 개념입니다');
  chk('새 탭에서도 03절이 맨 위', await tab.evaluate(() => {
    const t = document.getElementById('s03').getBoundingClientRect().top; return t >= 0 && t <= 40; }), true);
  const closed = tab.waitForEvent('close', { timeout: 3000 }).then(() => true, () => false);
  await tab.click('.dtb__go');
  chk('누르면 그 탭이 닫힌다(성적표 탭이 남는다)', await closed, true);
  chk('성적표 탭은 그대로다', await dtPage.evaluate(() => !!document.getElementById('dt')), true);
  await ctx1.close();

  /* 2) 닫기를 막는 브라우저 · 뒤로 갈 곳이 있으면 뒤로 */
  const ctx2 = await browser.newContext();
  await stubDT(ctx2);
  await ctx2.addInitScript(() => { window.close = function () {}; });
  const p2 = await open(ctx2);
  await p2.goto(BASE + 'lecture-index.html', { waitUntil: 'domcontentloaded' });
  await p2.goto(BASE + LEC + '?from=dt&c=gc&r=3#s02', { waitUntil: 'load' });
  chk('뒤로 갈 곳이 있다', await p2.evaluate(() => history.length > 1), true);
  await p2.click('.dtb__go');
  await p2.waitForURL(u => !/lec-078/.test(String(u)), { timeout: 3000 }).catch(() => {});
  chk('못 닫으면 뒤로 간다', p2.url(), BASE + 'lecture-index.html');

  /* 3) 닫기를 막는 브라우저 · 새 탭이라 뒤로 갈 곳도 없으면 DT 성적표 첫 화면으로 */
  const d3 = await open(ctx2);
  await d3.goto(DT, { waitUntil: 'load' });
  const [p3] = await Promise.all([ctx2.waitForEvent('page'), d3.click('#go')]);
  p3.on('pageerror', e => errs.push(e.message));
  await p3.waitForLoadState('load');
  chk('새 탭은 기록이 한 칸이다', await p3.evaluate(() => history.length), 1);
  await p3.click('.dtb__go');
  await p3.waitForURL(u => !/lec-078/.test(String(u)), { timeout: 3000 }).catch(() => {});
  chk('뒤로 갈 곳이 없으면 DT 성적표로 (학생 코드 없이)', p3.url(), DT);
  chk('탭은 열려 있다(닫기가 막혔으니)', p3.isClosed(), false);
  await ctx2.close();

  chk('자바스크립트 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})();
