/* ============================================================
   화면 258장을 전부 열어 본다
   ------------------------------------------------------------
   낱개 검사는 저마다 한 화면의 한 가지 일을 본다. 그런데 화면이 **열리다가
   터지는 것**은 아무도 안 본다. 자바스크립트가 한 줄 어긋나면 그 아래가
   통째로 안 돌아가는데, 파일은 멀쩡히 있고 링크도 살아 있어서 정적 검사는
   전부 초록불이다.

   실제로 이 저장소에는 그런 검사가 없었다. 회차를 넣고 팔레트를 바꾸고
   목차를 고치는 동안, "그래서 화면이 열리기는 하는가" 를 확인한 것은
   사람이 눈으로 본 몇 장뿐이었다.

   여기서 보는 것은 둘뿐이고, 둘 다 **거짓 경보가 나기 어려운 것**이다.

     ① 화면이 던지는 자바스크립트 오류가 있는가 (pageerror)
     ② 같은 서버에 없는 파일을 달라고 하는가 (4xx·5xx)

   바깥 주소(구글 글꼴·앱스스크립트 창구)는 **안 센다.** 검사 기계에는
   인터넷이 없고, 글꼴은 tools/font_block.py 가 이미 그리기를 안 막게
   만들어 두었다. 바깥이 안 닿는 것을 여기서 빨간불로 만들면 매번 빨간불이
   되고, 그러면 아무도 안 본다.

   실행:  PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/page-health.js
   (저장소 루트에서 python3 -m http.server 8931 이 떠 있어야 한다)
   ============================================================ */
'use strict';
const noSheet = require('./_nosheet.js');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const BASE = 'http://127.0.0.1:8931/';
const LANES = 4;                 // 한꺼번에 여는 창 수. 늘리면 빨라지고 시끄러워진다

(async () => {
  const mod = process.env.PLAYWRIGHT_MODULE;
  if (!mod) { console.log('SKIP  playwright 없음'); process.exit(0); }
  const { chromium } = require(mod);

  const files = fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).sort();
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
  /* ⚠ **시트를 막고 시작한다.** 안 막으면 검사가 학원의 진짜 시트를 읽고,
     채점하는 검사는 **거기에 줄을 쓴다.** 2026-08-12 에 실제로 그랬다 —
     이 검사가 판을 돌 때마다 «무응답점검·분류점검·자료링크점검» 같은 이름이
     선생님 시트에 쌓이고 있었다(POST 를 세어서 확인했다).
     `tests/_nosheet.js` 머리말이 처음부터 이르던 일이다. */
  await noSheet(browser);
  const bad = [];

  const visit = async (ctx, f) => {
    const p = await ctx.newPage();
    const errs = [], miss = [];
    p.on('pageerror', e => errs.push(String(e).split('\n')[0].slice(0, 150)));
    p.on('response', r => {
      if (r.status() >= 400 && r.url().startsWith(BASE)) {
        miss.push(r.status() + ' ' + decodeURIComponent(r.url().slice(BASE.length)));
      }
    });
    try {
      await p.goto(BASE + encodeURIComponent(f), { waitUntil: 'domcontentloaded', timeout: 20000 });
      await p.waitForTimeout(600);
    } catch (e) {
      errs.push('열지 못했다: ' + String(e).split('\n')[0].slice(0, 90));
    }
    await p.close();
    if (errs.length || miss.length) {
      bad.push({ f, errs: [...new Set(errs)].slice(0, 3), miss: [...new Set(miss)].slice(0, 5) });
    }
  };

  const queue = files.slice();
  await Promise.all(Array.from({ length: LANES }, async () => {
    const ctx = await browser.newContext();
    while (queue.length) await visit(ctx, queue.shift());
    await ctx.close();
  }));
  await browser.close();

  console.log('  열어 본 화면 ' + files.length + '장');
  if (bad.length) {
    bad.sort((a, b) => a.f.localeCompare(b.f));
    for (const o of bad) {
      console.log('  FAIL  ' + o.f);
      o.errs.forEach(e => console.log('          오류  ' + e));
      o.miss.forEach(m => console.log('          없음  ' + m));
    }
    console.log('\n' + bad.length + '장이 열리다가 말썽을 냈다');
    process.exit(1);
  }
  console.log('  PASS  모두 조용히 열린다 (자바스크립트 오류 0 · 없는 파일 요청 0)');
})();
