/* ============================================================
   바깥 글꼴이 첫 화면을 인질로 잡지 않는다
   ------------------------------------------------------------
   브라우저는 `<link rel=stylesheet>` 를 만나면 **그리기를 멈추고 기다린다.**
   그 stylesheet 가 구글에서 오면, 구글이 늦거나 안 닿는 동안 화면은 '글꼴만
   못생긴 상태' 가 아니라 **아무것도 없는 흰 종이**다.

   재어 보니 이랬다(3G · CPU 4배 느리게 · 구글이 대답하지 않는 망).

       index.html   첫 그림  13,184 ms    ← 바깥 글꼴을 기다린다
       hub.html     첫 그림     504 ms    ← 이 줄이 없다
       final.html   첫 그림     584 ms    ← 이 줄이 없다

   같은 저장소·같은 망·같은 브라우저다. 차이는 그 한 줄뿐이었다.
   고친 뒤 index.html 은 **856 ms**.

   여기서 지키는 것:
   - 구글이 **아예 대답하지 않아도** 첫 화면이 뜬다
   - 구글이 대답하면 글꼴이 **그대로 적용된다** (미룬 것이지 버린 것이 아니다)
   - 자바스크립트가 꺼져 있어도 글꼴을 받는다 (noscript 짝이 있다)
   - 첫 화면 셋(index·hub·final) 어디에도 막는 바깥 글꼴이 없다

   ⚠ 빠르기만 재면 '글꼴을 통째로 빼는 것' 이 만점을 받는다. 그래서 **오는지**
     를 같이 잰다. 둘 중 하나만 보면 검사가 거짓말을 한다.

   실행:
       node tests/first-paint.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const noSheet = require('./_nosheet.js');
/* 포트를 그 자리에서 받고, 서버가 **대답할 때까지** 기다린다.
   고정 포트를 박아 두면 검사 두 벌이 겹칠 때 뒤엣것이 빈 화면을 보고
   "그게 화면에 없다" 고 말한다 — tests/_serve.js 머리말. */
const { serve } = require('./_serve.js');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
/* 번호를 안 박는다(0 이면 빈 포트를 받는다). `PORT` 를 준 자리는 그대로 쓴다.
   **서버를 띄운 뒤 실제로 받은 번호로 채운다** — 아래 `serve()` 바로 다음. */
let PORT = Number(process.env.PORT || 0);
const ROOT = path.join(__dirname, '..');
/* ── 네 앱이 **같은 천장**을 쓴다 ──────────────────────────────
   exam · DT · KMChC · study64 넷 다 `PAINT_MAX = 4000` 이다.
   2026-08-11, 넷을 **겹치지 않게 하나씩** 세 번씩 재어 맞춘 값이다(#42).
   여기는 그전까지 혼자 2,500 이었다 — 올려서 맞췄다.

       DT        report   388 · index   348
       exam      index    772 · hub     504 · final 608
       KMChC     report 1,424 · answers 1,348 · index (FCP 없음 · 첫 칠 924)
       study64   index  1,464 · report 1,188 · answers 776

   성한 값은 넷 다 1.5초 아래다. 숫자만 보면 2,500 이 맞다. 그런데 넷을
   잇달아 재던 첫 판에서 KMChC report 이 3,020ms 로 나왔다 — 같은 것을
   조용할 때 세 번 다시 재니 1,328 · 1,336 · 1,424 였다. 기계가 바쁘면 성한
   쪽이 두 배로 늘어난다(여기 index 도 772 → 1,320 이었다). 천장은 **목표가
   아니라 걸림줄**이고, 성한 판에서 울리는 걸림줄은 다음부터 아무도 안 본다.

   이 줄이 잡는 병은 13,184ms 였다 — 바깥 글꼴이 첫 화면을 인질로 잡는 것.
   4,000 은 그 병과 **바쁜 판의 성한 값** 사이에 있고, 2,500 은 그 사이가
   아니라 성한 값 위에 걸친다.

   ⚠ 한 곳을 고치면 **네 곳을 같이 고친다.** 한 저장소만 낮추면 나머지 셋은
     낮춘 줄 모른 채 초록불이다 — 그러면 «맞춰 두었다» 는 말이 거짓이 된다.
   ───────────────────────────────────────────────────────────── */
const PAINT_MAX = 4000;

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

/* 아주 작은 글꼴 CSS. 진짜 글꼴 파일은 안 받는다 — 여기서 볼 것은 '이 줄이
   화면에 닿느냐' 이지 글자 모양이 아니다. */
const FAKE_CSS = ':root{--font-arrived:1}';

async function open(browser, { answerFonts }) {
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Network.emulateNetworkConditions', {
    offline: false, downloadThroughput: 1.6 * 1024 * 1024 / 8,
    uploadThroughput: 750 * 1024 / 8, latency: 150 });
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  /* 글꼴 창구. 대답하지 않는 망을 흉내 낼 때는 **아무 답도 주지 않는다** —
     끊어 버리면(abort) 브라우저가 곧바로 포기하므로 기다림이 재현되지 않는다. */
  await p.route('**://fonts.googleapis.com/**', route => {
    if (!answerFonts) return;                       // 영원히 매달아 둔다
    return route.fulfill({ status: 200, contentType: 'text/css', body: FAKE_CSS });
  });
  await p.route('**://fonts.gstatic.com/**', route => {
    if (!answerFonts) return;
    return route.fulfill({ status: 200, contentType: 'font/woff2', body: '' });
  });
  await p.route('**://script.google.com/**', route => route.fulfill({
    status: 200, contentType: 'text/javascript',
    body: (new URL(route.request().url()).searchParams.get('callback') || 'cb') + '({"ok":true});' }));
  return { ctx, p };
}

const paintOf = p => p.evaluate(() => {
  const e = performance.getEntriesByType('paint')
    .find(x => x.name === 'first-contentful-paint');
  return e ? Math.round(e.startTime) : -1;
});

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(
    Object.assign({ args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(browser);

  try {
    console.log('── 구글이 대답하지 않는 망 ──');
    for (const page of ['index.html', 'hub.html', 'final.html']) {
      const { ctx, p } = await open(browser, { answerFonts: false });
      await p.goto(`http://localhost:${PORT}/${page}`,
                   { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      const fcp = await paintOf(p);
      console.log(`  ${page} 첫 그림 ${fcp}ms`);
      chk(`${page} 이 글꼴을 기다리지 않는다`, fcp > 0 && fcp < PAINT_MAX, true);
      await ctx.close();
    }

    console.log('\n── 구글이 대답하는 망 (미룬 것이지 버린 것이 아니다) ──');
    {
      const { ctx, p } = await open(browser, { answerFonts: true });
      await p.goto(`http://localhost:${PORT}/index.html`,
                   { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      /* onload 에서 media 가 all 로 돌아와야 글꼴이 화면에 닿는다. */
      const ok = await p.waitForFunction(() => {
        const L = [...document.querySelectorAll('link[rel=stylesheet]')]
          .filter(l => /fonts\.googleapis\.com/.test(l.href));
        return L.length > 0 && L.every(l => l.media === 'all');
      }, null, { timeout: 20000 }).then(() => true).catch(() => false);
      chk('글꼴이 도착하면 화면에 적용된다', ok, true);
      const arrived = await p.evaluate(() =>
        getComputedStyle(document.documentElement).getPropertyValue('--font-arrived').trim());
      chk('글꼴 CSS 가 실제로 읽혔다', arrived, '1');
      await ctx.close();
    }

    console.log('\n── 자바스크립트가 꺼져 있어도 ──');
    {
      /* ⚠ 자바스크립트를 끄면 evaluate 자체가 안 돈다 — 브라우저 안에서
         '적용됐나' 를 물어볼 길이 없다. 그래서 **짝이 있는가**를 본다.
         <noscript> 안의 것이 스크립트 없는 브라우저에서 살아난다는 것은
         브라우저의 정해진 동작이라 여기서 다시 잴 일이 아니다. 여기서 틀릴 수
         있는 것은 '짝을 안 넣었다' 뿐이고, 그건 이렇게 잡힌다. */
      const { ctx, p } = await open(browser, { answerFonts: true });
      await p.goto(`http://localhost:${PORT}/index.html`,
                   { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      const pair = await p.evaluate(() => {
        const deferred = [...document.querySelectorAll('link[rel=stylesheet]')]
          .filter(l => /fonts\.googleapis\.com/.test(l.href))
          .map(l => l.getAttribute('href'));
        const inNoscript = [...document.querySelectorAll('noscript')]
          .map(n => n.textContent || '').join(' ');
        return { n: deferred.length,
                 covered: deferred.filter(h => inNoscript.includes(h)).length };
      });
      console.log(`  미룬 글꼴 ${pair.n}곳 · noscript 짝이 있는 것 ${pair.covered}곳`);
      chk('미룬 글꼴에는 반드시 noscript 짝이 있다', pair.n > 0 && pair.covered === pair.n, true);
      await ctx.close();
    }
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
