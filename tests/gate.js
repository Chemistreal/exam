/* ============================================================
   첫 화면 잠금 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   이 페이지들은 GitHub Pages 에 그대로 올라간다. 주소만 알면 아무나 들어와
   학생 이름과 점수를 볼 수 있어서, 들어올 때 코드를 한 번 묻는다.

   **이것은 암호가 아니다.** 소스 보기를 누르면 코드가 그대로 보인다.
   지나가다 눌러 보는 사람을 막는 문고리다. 그래서 이 검사도 "뚫리지
   않는가"가 아니라 "**막아야 할 것을 막고, 막으면 안 되는 것을 안 막는가**"
   를 본다. 후자가 더 위험하다 — 학부모가 성적표를 못 열면 바로 사고다.

   여기서 지키는 것:
   - 교사용 세 페이지(index.html · final.html · hub.html)는 코드를 묻는다
   - 셋은 **같은 열쇠칸**을 쓴다(한 곳에서 맞히면 나머지도 열린다) — 셸은
     파이널을 iframe 으로 얹으므로, 갈라져 있으면 화면이 두 겹으로 잠긴다
   - 틀린 코드로는 안 열린다
   - 맞히면 열리고, 새로고침해도 다시 묻지 않는다
   - **학부모 성적표 링크(#r=…)는 묻지 않는다**
   - **학생 답안 제출 페이지는 묻지 않는다**
   - 열린 뒤 스크롤이 다시 살아난다(잠금이 overflow:hidden 을 걸어 둔다)

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/gate.js
   ============================================================ */
'use strict';
/* 멈추는 검사는 실패하는 검사보다 나쁘다 — tests/_watchdog.js 주석 참고. */
require('./_watchdog.js')(240);
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const AT = p => `http://localhost:${PORT}/${p}`;
const CODE = '0000';
// 실제로 보낸 성적표 링크 모양(#r=시험.답안..이름)
const SHARED = 'final.html#r=jmchc-6.lh0dhl0zzuxkmg3q98nuun7oshe..~6rmA7KeA7ISx';

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
/* 검사가 운영 시트를 읽으면 실 데이터가 심어 둔 데이터를 덮는다.
   실제로 CI 에서 그렇게 깨졌다 — tests/_nosheet.js 의 주석 참고. */
const noSheet = require('./_nosheet.js');
/* 검사가 진짜 시트에 쓰면 안 된다. 실제로 CI 가 돌 때마다 파이널 앱이
   진짜 앱스크립트로 제출해서, 홍길동·예비본 같은 줄이 학생들 석차
   모집단에 섞여 들어갔다. 브라우저를 띄우자마자 그 길을 끊는다. */
const seal = require('./_seal.js');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

(async () => {
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  /* ⚠ 브라우저에 건다 — 화면 하나에 걸면 나중에 여는 화면이 샌다. */
  await noSheet(browser);
  const errs = [];
  // 방문마다 새 컨텍스트 — localStorage 가 남으면 두 번째부터 안 묻는다
  const visit = async (path, wait) => {
    const page = await (await browser.newContext()).newPage();
    page.on('pageerror', e => errs.push(path + ': ' + e.message));
    await page.goto(AT(path), { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(wait || 900);
    return page;
  };
  const locked = page => page.evaluate(() => !!document.getElementById('gate'));

  console.log('── 교사용 페이지는 묻는다 ──');
  // 통합 셸도 반 명단·점수를 그대로 보여 준다 — 같이 묻는다
  for (const path of ['index.html', 'final.html', 'hub.html']) {
    const page = await visit(path);
    chk(`${path} 잠긴다`, await locked(page), true);
    await page.close();
  }

  console.log('\n── 열쇠칸을 나눠 쓴다 ──');
  {
    /* 셸은 파이널을 iframe 으로 얹는다. 열쇠칸이 갈라져 있으면 셸에서 한 번
       넣고, 그 안의 파이널이 또 물어 화면이 두 겹으로 잠긴다. */
    const page = await visit('final.html');
    await page.fill('#gateIn', CODE);
    await page.click('#gateGo');
    await page.waitForTimeout(900);
    await page.goto(AT('hub.html'), { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(900);
    chk('파이널에서 맞히면 셸도 열린다', await locked(page), false);
    await page.close();
  }

  console.log('\n── 틀린 코드 ──');
  {
    const page = await visit('final.html');
    await page.fill('#gateIn', '1234');
    await page.click('#gateGo');
    await page.waitForTimeout(250);
    chk('안 열린다', await locked(page), true);
    chk('틀렸다고 알려 준다', await page.evaluate(() => document.getElementById('gateErr').textContent), '코드가 맞지 않습니다.');
    chk('입력칸을 비운다', await page.evaluate(() => document.getElementById('gateIn').value), '');
    // 코드를 기억해 두지 않았는지 — 틀렸는데 통과 표시가 남으면 다음에 그냥 열린다
    chk('통과 표시가 안 남는다', await page.evaluate(() => localStorage.getItem('chemistreal:gate')), null);
    await page.close();
  }

  console.log('\n── 맞는 코드 ──');
  {
    const page = await visit('final.html');
    await page.fill('#gateIn', CODE);
    await page.click('#gateGo');
    await page.waitForTimeout(1500);
    chk('열린다', await locked(page), false);
    chk('스크롤이 살아난다', await page.evaluate(() => document.documentElement.style.overflow), '');
    chk('앱이 그대로 뜬다', await page.evaluate(() => /명단 관리|시험/.test(document.body.innerText)), true);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(900);
    chk('새로고침해도 안 묻는다', await locked(page), false);
    await page.close();
  }
  {
    // 엔터로도 들어가진다(버튼을 안 누르는 사람이 있다)
    const page = await visit('index.html');
    await page.fill('#gateIn', CODE);
    await page.press('#gateIn', 'Enter');
    await page.waitForTimeout(700);
    chk('엔터로도 열린다', await locked(page), false);
    await page.close();
  }

  console.log('\n── 막으면 안 되는 것 ──');
  {
    const page = await visit(SHARED, 2500);
    chk('학부모 성적표 링크는 안 묻는다', await locked(page), false);
    chk('성적표가 보인다', await page.evaluate(() => /석차|백분위|정답률/.test(document.body.innerText)), true);
    await page.close();
  }
  {
    const page = await visit('final-submit.html');
    chk('학생 답안 제출은 안 묻는다', await locked(page), false);
    await page.close();
  }

  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
