/* ============================================================
   휴대폰 폭(360px)에서 화면이 옆으로 밀리지 않는가
   ------------------------------------------------------------
   여태 아무도 이걸 안 쟀다. `tools/audit_pages.py` 는 viewport 태그가
   **있는지**만 본다 — 태그가 있어도 안이 넘치면 화면은 옆으로 밀린다.
   네 저장소 어디에도 이 자가 없었다(`docs/앱별-전수조사.md` 4절).

   처음 재어 보니 258장 가운데 **열여섯 장**이 걸렸다(2026-08-10).

       강의 14장    span.fm  — 수식이 한 줄로 뻗어 문서가 598px 까지 벌어졌다
       강의  2장    table    — 칸이 다섯인 표(435px)

   학생이 **휴대폰으로 읽는 강의**다. 글을 읽다가 화면이 좌우로 흔들렸다.

   수식은 줄을 바꾸면 못 읽는다(`.fm{white-space:nowrap}` 은 일부러 그렇게
   둔 것이다). 표도 칸을 줄이면 말하려던 것이 달라진다. 그래서 **둘 다 그대로
   두고** 제자리에서 옆으로 구르게 했다 — DT 의 OMR 시트와 같은 손질이다.

   무엇을 걸고 무엇을 안 거는가
   ---------------------------
   스스로 `overflow-x: auto` 를 걸어 둔 상자 **안**에서 넘치는 것은 안 잡는다.
   그건 "옆으로 굴러라" 라고 정해 둔 자리다. 잡는 것은 그 밖으로 삐져나와
   **문서 전체를 옆으로 미는** 것뿐이다 — 그때 학부모는 글을 읽다가 화면이
   좌우로 흔들리는 것을 본다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/narrow.js
   ============================================================ */
'use strict';
/* 포트를 그 자리에서 받고, 서버가 **대답할 때까지** 기다린다.
   고정 포트를 박아 두면 검사 두 벌이 겹칠 때 뒤엣것이 빈 화면을 보고
   "그게 화면에 없다" 고 말한다 — tests/_serve.js 머리말. */
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');
const fs = require('fs');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
/* 번호를 안 박는다(0 이면 빈 포트를 받는다). `PORT` 를 준 자리는 그대로 쓴다.
   **서버를 띄운 뒤 실제로 받은 번호로 채운다** — 아래 `serve()` 바로 다음. */
let PORT = Number(process.env.PORT || 0);
const ROOT = path.join(__dirname, '..');
const WIDTH = 360;          // 아이폰 SE·갤럭시 A 계열의 논리 폭

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
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const pages = fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).sort();
  const browser = await chromium.launch(Object.assign(
    { args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {}));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(browser);

  const bad = [];
  try {
    for (const name of pages) {
      const ctx = await browser.newContext({ viewport: { width: WIDTH, height: 740 },
                                             serviceWorkers: 'block' });
      // 검사가 진짜 시트에 쓰면 안 된다 — 구글로 나가는 길을 끊는다.
      await ctx.route('**://script.google.com/**', r => r.abort());
      const p = await ctx.newPage();
      p.on('pageerror', () => {});
      try {
        /* 넉넉히 기다린다. exam 은 화면이 258장이고 그중 index.html 은
           시험 목록을 받아 그리느라 20초에 안 끝난 적이 있다 — 그때 이 자는
           '열다 터짐' 이라고 말했다. 못 여는 것과 넘치는 것은 다른 일이다. */
        await p.goto(`http://localhost:${PORT}/${encodeURIComponent(name)}`,
                     { waitUntil: 'load', timeout: 45000 });
        await p.waitForTimeout(350);
        const r = await p.evaluate(() => {
          const d = document.documentElement;
          if (d.scrollWidth <= d.clientWidth + 1) return null;
          const over = [];
          for (const el of document.querySelectorAll('body *')) {
            const b = el.getBoundingClientRect();
            if (!(b.width > 0 && b.right > d.clientWidth + 1)) continue;
            // 스스로 구르게 해 둔 상자 안이면 넘어간다 — 그건 정해 둔 자리다
            let anc = el, rolled = false;
            while (anc) {
              const a = getComputedStyle(anc);
              if (a.overflowX === 'auto' || a.overflowX === 'scroll') { rolled = true; break; }
              anc = anc.parentElement;
            }
            if (rolled) continue;
            over.push(el.tagName.toLowerCase() +
              (typeof el.className === 'string' && el.className.trim()
                ? '.' + el.className.trim().split(/\s+/)[0] : ''));
          }
          return over.length ? { doc: d.scrollWidth, view: d.clientWidth,
                                 over: [...new Set(over)].slice(0, 5) } : null;
        });
        if (r) bad.push([name, r]);
      } catch (e) {
        bad.push([name, { err: String(e).slice(0, 90) }]);
      }
      await ctx.close();
    }
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(`\n화면 ${pages.length}장 · ${WIDTH}px 에서 옆으로 밀리는 장 ${bad.length}장`);
  for (const [n, r] of bad) {
    if (r.err) { console.log(`  FAIL  ${n}  (열다 터짐) ${r.err}`); continue; }
    console.log(`  FAIL  ${n}  문서 ${r.doc}px > 화면 ${r.view}px`);
    for (const o of r.over) console.log(`          ${o}`);
  }
  if (bad.length) {
    console.log('\n종이로 뽑는 시트처럼 폭을 줄일 수 없는 것이면, 종이는 그대로 두고');
    console.log('좁은 화면에서만 그 상자가 `overflow-x:auto` 로 구르게 한다.');
    process.exit(1);
  }
  console.log('  PASS  모든 화면이 휴대폰 폭 안에 들어간다');
  process.exit(0);
})();
