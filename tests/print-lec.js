/* ============================================================
   강의록은 종이에서도 읽혀야 한다 — 흰 종이에 흰 글씨가 아니라
   ------------------------------------------------------------
   강의록(lec-*.html) 125장은 수업 때 나눠 주는 **종이가 본업**이다.
   그런데 화면용으로만 지어져 있었다.

       header{background:linear-gradient(180deg,#0E5A4C,#0b4a3f);color:#fff}
       .sec__no{background:var(--teal);color:#fff}

   브라우저는 인쇄할 때 **배경을 기본으로 안 찍는다** — 잉크를 아끼려고
   그렇게 되어 있고, '배경 그래픽' 을 사람이 따로 켜야 나온다. 그러면
   초록 배경은 안 찍히고 그 위의 흰 글씨만 남는다. 흰 종이에 흰 글씨다.

     · 강의록 제목이 통째로 안 보인다 — 125장 전부
     · 절 번호가 전부 안 보인다 — 601곳

   화면으로 보면 멀쩡하다. 종이에서만 사라지니 아무도 몰랐다.

   여기서 지키는 것:
   - 인쇄 매체에서 제목·절 번호가 흰색이 아니다 (종이에서 읽힌다)
   - 화면 매체에서는 **하나도 안 바뀐다** (원래 초록 머리띠 그대로)

   ⚠ 배경이 실제로 찍히느냐는 브라우저 설정이라 잴 수 없다. 그래서 잴 수
     있는 것으로 잰다 — **배경이 안 찍혀도 글씨가 읽히는가.**

   실행:
       node tests/print-lec.js
   (playwright 와 크로미움 경로가 필요하다.)
   ============================================================ */
'use strict';
const seal = require('./_seal.js');
/* 포트를 그 자리에서 받고, 서버가 **대답할 때까지** 기다린다.
   고정 포트를 박아 두면 검사 두 벌이 겹칠 때 뒤엣것이 빈 화면을 보고
   "그게 화면에 없다" 고 말한다 — tests/_serve.js 머리말. */
const { serve } = require('./_serve.js');
const path = require('path');
const fs = require('fs');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
/* 번호를 안 박는다(0 이면 빈 포트를 받는다). `PORT` 를 준 자리는 그대로 쓴다.
   **서버를 띄운 뒤 실제로 받은 번호로 채운다** — 아래 `serve()` 바로 다음. */
let PORT = Number(process.env.PORT || 0);
const ROOT = path.join(__dirname, '..');

let fail = 0;
const chk = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + name +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* rgb(255,255,255) 인가. 흰 글씨는 흰 종이에서 안 보인다. */
const isWhite = c => /rgba?\(\s*25[0-5],\s*25[0-5],\s*25[0-5]/.test(String(c || ''));

/* 검사할 강의록. 앞·중간·끝에서 하나씩 골라 한 장만 고쳐 놓고 지나가는 일을 막는다. */
function pick() {
  const all = fs.readdirSync(ROOT)
    .filter(f => f.startsWith('lec-') && f.endsWith('.html')).sort();
  if (!all.length) return [];
  return [all[0], all[Math.floor(all.length / 2)], all[all.length - 1]];
}

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  /* 브라우저를 깔아 놓고도 조용히 건너뛰면 초록불이 거짓말이 된다. */
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  const page = await browser.newPage();

  try {
    for (const f of pick()) {
      console.log(`\n── ${f} ──`);
      await page.goto(`http://localhost:${PORT}/${f}`, { waitUntil: 'domcontentloaded' });

      const read = () => page.evaluate(() => {
        const g = sel => {
          const el = document.querySelector(sel);
          return el ? getComputedStyle(el).color : null;
        };
        return { h1: g('header h1'), no: g('.sec__no') };
      });

      /* 종이 — 배경이 안 찍혀도 읽혀야 한다 */
      await page.emulateMedia({ media: 'print' });
      const p = await read();
      chk('종이: 제목이 흰 글씨가 아니다', isWhite(p.h1), false);
      if (p.no !== null) chk('종이: 절 번호가 흰 글씨가 아니다', isWhite(p.no), false);

      /* 화면 — 하나도 안 바뀌어야 한다 */
      await page.emulateMedia({ media: 'screen' });
      const s = await read();
      chk('화면: 제목은 그대로 흰 글씨(초록 머리띠)', isWhite(s.h1), true);
    }
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
