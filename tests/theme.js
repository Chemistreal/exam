/* ============================================================
   같은 옷을 입힌 뒤에도 글씨가 읽히는가
   ------------------------------------------------------------
   `tools/theme.py` 가 화면 261장에 두 겹의 그림을 깔았다.

     · 머리띠 안에 새겨 넣은 분자 문양 (`header::after`)
     · 오른쪽 여백에 앉은 벤젠 고리 (`body` 의 background-image)

   둘 다 **글자 뒤에 깔릴 수 있다.** 그런데 화면을 글로만 읽는 검사
   (`tools/audit_pages.py`)는 이 둘을 못 본다 — CSS 규칙만 읽지, 겹쳐진
   결과를 안 보기 때문이다. 색 이름표만 재면 문양이 아무리 진해도 초록불이
   나온다. 통합 셸에서 이미 같은 함정을 밟았다.

   그래서 여기서는 **화면을 사진으로 찍어** 글자가 실제로 앉은 자리의 화소를
   읽는다. 찍기 전에 글자만 투명하게 만든다 — 안 그러면 글자 획이 같이 찍혀
   '바탕' 이 아니라 글자색을 재게 된다.

   갈래마다 한 장씩 본다. 한 장만 재면 나머지는 안 재는 것과 같다.

   실행:
       NODE_PATH=tests/node_modules node tests/theme.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(300);
const seal = require('./_seal.js');
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

/* 갈래마다 한 장. 띠가 있는 것 · 없는 것, 종이색이 달랐던 것을 고루 넣는다. */
const PAGES = [
  ['lec-001-atomic-structure-isotopes.html', '개념강의 (띠 있음)'],
  ['mirt.html',                              '분석 도구 (띠 있음)'],
  ['sol-final-jmchc-5.html',                 '해설지 (띠 없음)'],
  ['paper-chem2-1.html',                     '문제지 (띠 없음)'],
  ['admin.html',                             '교사 콘솔 (종이색이 달랐던 무리)'],
  ['index_haeseol.html',                     '해설 목록'],
];

let fail = 0;
const chk = (n, ok, extra) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (extra ? '  ' + extra : ''));
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

/* 글자가 앉은 자리의 **합쳐진** 화소를 읽어 최악의 대비를 낸다. */
async function measure(p) {
  const nodes = await p.evaluate(() => {
    const out = [];
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set();
    let t;
    while ((t = walk.nextNode())) {
      const s = (t.nodeValue || '').trim();
      if (s.length < 2) continue;
      const el = t.parentElement;
      if (!el || seen.has(el)) continue;
      if (/^(SCRIPT|STYLE|NOSCRIPT|OPTION)$/.test(el.tagName)) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      /* ⚠ 금박 글씨(배경 그라데이션을 글자 모양으로 오려 쓰는 것)는 여기서 안 잰다.
         그런 글자는 computed color 가 **검정으로 남고** 실제로 칠해지는 것은
         그라데이션이라, 그대로 재면 '검정 글씨' 대 '옥색 바탕' 이 되어 멀쩡한
         제목이 빨간불이 된다. 이건 다른 방법으로 재야 하는 것이라 건너뛴다. */
      if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)' ||
          /text/.test(cs.webkitBackgroundClip || '') ||
          /text/.test(cs.backgroundClip || '')) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) continue;
      if (r.bottom < 0 || r.top > innerHeight) continue;     // 첫 화면만 — 사진이 거기까지다
      seen.add(el);
      const size = parseFloat(cs.fontSize);
      out.push({
        tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
        text: s.slice(0, 18),
        x: r.left, y: r.top, w: r.width, h: r.height, fg: cs.color,
        /* 24px 이상 또는 18.66px 굵은 글씨는 큰 글씨(3:1), 나머지는 본문(4.5:1) */
        need: (size >= 24 || (size >= 18.66 && Number(cs.fontWeight) >= 700)) ? 3 : 4.5,
      });
      if (out.length >= 140) break;
    }
    return out;
  });

  await p.addStyleTag({ content: '*{color:transparent !important;text-shadow:none !important}' });
  await p.waitForTimeout(300);
  const png = (await p.screenshot()).toString('base64');

  return p.evaluate(async ({ png, nodes }) => {
    const bmp = await createImageBitmap(await (await fetch('data:image/png;base64,' + png)).blob());
    const cv = document.createElement('canvas');
    cv.width = bmp.width; cv.height = bmp.height;
    cv.getContext('2d').drawImage(bmp, 0, 0);
    const px = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
    const at = (x, y) => {
      const i = (Math.min(cv.height - 1, Math.max(0, Math.round(y))) * cv.width +
                 Math.min(cv.width - 1, Math.max(0, Math.round(x)))) * 4;
      return [px[i], px[i + 1], px[i + 2]];
    };
    const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    const L = q => 0.2126 * f(q[0]) + 0.7152 * f(q[1]) + 0.0722 * f(q[2]);
    const parse = s => { const m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return null;
      const a = m[1].split(/[,\s/]+/).map(Number); return [a[0], a[1], a[2]]; };

    let worst = null; const all = [];
    for (const nd of nodes) {
      const fg = parse(nd.fg); if (!fg) continue;
      const lf = L(fg);
      let w = 99, bg = null;
      /* ⚠ 상자의 **모서리를 안 잰다.** 알약 모양 단추·배지는 모서리가 둥글어서
         네 귀퉁이가 단추 밖(종이색)이다. 거기서 재면 흰 글씨 대 종이색이 되어
         1.0:1 이 나온다 — 멀쩡한 단추가 죄다 빨간불이 된다. 안쪽만 훑는다. */
      for (let gy = 0; gy <= 4; gy++) for (let gx = 0; gx <= 10; gx++) {
        const q = at(nd.x + nd.w * (0.18 + 0.64 * gx / 10),
                     nd.y + nd.h * (0.28 + 0.44 * gy / 4));
        const lb = L(q);
        const c = (Math.max(lf, lb) + 0.05) / (Math.min(lf, lb) + 0.05);
        if (c < w) { w = c; bg = q; }
      }
      const slack = Math.round((w - nd.need) * 100) / 100;
      const row = { slack, r: Math.round(w * 100) / 100, need: nd.need,
                    tag: nd.tag, text: nd.text, bg, fg };
      all.push(row);
      if (!worst || slack < worst.slack) worst = row;
    }
    all.sort((a, b) => a.slack - b.slack);
    return { n: nodes.length, worst, bad: all.filter(x => x.slack < 0).slice(0, 6) };
  }, { png, nodes });
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(Object.assign(
    { args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {})));

  try {
    for (const [file, label] of PAGES) {
      const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 },
                                             serviceWorkers: 'block' });
      const p = await ctx.newPage();
      const errs = [];
      p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
      await p.addInitScript(() => {
        try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
      });
      await p.goto(`http://localhost:${PORT}/${file}`, { waitUntil: 'load' });
      await p.waitForTimeout(900);

      /* 옷을 실제로 입고 있는가 — 규칙만 있고 안 그려지면 뜻이 없다. */
      const on = await p.evaluate(() => {
        const st = document.getElementById('ct-theme');
        const bg = getComputedStyle(document.body).backgroundImage;
        return { has: !!st, v: st && st.dataset.v, fam: st && st.dataset.fam,
                 want: st && st.dataset.seal,
                 seal: /svg/i.test(bg),
                 bodyL: (() => { const m = /rgba?\(([^)]+)\)/
                     .exec(getComputedStyle(document.body).backgroundColor);
                   if (!m) return 1; const a = m[1].split(/[,\s/]+/).map(Number);
                   const f = c => { c /= 255; return c <= 0.03928 ? c/12.92
                     : Math.pow((c+0.055)/1.055, 2.4); };
                   return 0.2126*f(a[0]) + 0.7152*f(a[1]) + 0.0722*f(a[2]); })(),
                 ink: getComputedStyle(document.documentElement)
                        .getPropertyValue('--ink').trim().toLowerCase() };
      });
      console.log(`\n── ${label} · ${file} ──`);
      chk('같은 옷을 입고 있다', on.has && on.v === '4', on.fam ? '갈래 ' + on.fam : '');
      /* 팔레트가 한 벌인지는 **화면이 실제로 쓰는 값**으로 본다. */
      const dark = on.bodyL < 0.18;
      if (dark) console.log('      (스스로 어두운 화면 — 팔레트·표식은 일부러 안 씌운다)');
      if (!dark) chk('먹색이 한 벌이다', on.ink === '#23201b', on.ink);
      /* 표식은 **얹기로 한 화면에서만** 요구한다. 스스로 어두운 화면이나 이미
         제 배경 그림이 있는 화면에는 일부러 안 얹는다 — 그걸 여기서 요구하면
         '남의 결을 안 덮는다' 는 규칙을 검사가 되돌리게 된다. */
      if (on.want === '1') chk('여백에 표식이 앉았다', on.seal, '');
      else console.log('      (제 배경이 있거나 어두운 화면 — 표식은 일부러 안 얹는다)');

      const m = await measure(p);
      const w = m.worst;
      chk('그림 위에서도 글씨가 읽힌다',
          !!w && w.r >= w.need,
          w ? `가장 나쁜 자리 ${w.r}:1 (기준 ${w.need}) · ${w.tag} "${w.text}" · 바탕 rgb(${w.bg.join(',')})` : '잰 글자 없음');
      /* 한 글자도 안 재고 통과하는 것을 막는다. */
      (m.bad || []).forEach(b => console.log(
        `      · ${b.r}:1 (기준 ${b.need}) ${b.tag} "${b.text}" 글씨 ${b.fg} 바탕 rgb(${b.bg.join(',')})`));
      chk('글자를 실제로 쟀다', m.n >= 3, m.n + '마디');
      chk('콘솔에 예외가 없다', !errs.length, errs[0] || '');
      await ctx.close();
    }
  } finally {
    await browser.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
