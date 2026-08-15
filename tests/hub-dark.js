/* ============================================================
   **어두운 옷에서도 읽힌다** — 눈이 아니라 자로 잰다 (브라우저 필요)
   ------------------------------------------------------------
   2026-08-15. 재어 보니 이 저장소 화면 258장 **어디에도 어두운 옷이
   없었다.** 선생님은 밤에 채점하신다.

   ⚠ 이 저장소는 **팔레트를 덮었다가 화면 하나를 망가뜨린 적이 있다.**
     DT 의 `roster.html` 은 일부러 어두운 화면이었는데 거기에 어두운 먹색을
     씌워 어두운 바탕에 어두운 글씨, **1.14:1** 이 됐다(tools/theme.py 머리말).
     그래서 여기서는 «예뻐 보인다» 로 넘어가지 않고 **화면에 실제로 그려진
     글자마다 색을 읽어 대비를 잰다.**

   여기서 지키는 것
   ----------------
     · 아무것도 안 고르면 **기계 설정을 따른다** (밤에 저절로 어두워진다)
     · 고른 것은 **기계보다 세다** — 기계가 어두워도 «밝게» 면 밝다
     · 고른 것이 **다음에도 남는다** (이 브라우저에만)
     · 어두운 옷에서 본문 **4.5:1** · 큰 글씨 **3:1** 을 지킨다
     · 밝은 옷은 **하나도 안 달라진다** — 있던 화면을 건드리지 않는다

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/hub-dark.js
   ============================================================ */
'use strict';
const path = require('path');
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH;
const ROOT = path.join(__dirname, '..');
let PORT = Number(process.env.PORT || 0);

let fail = 0;
const chk = (n, ok, extra) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (extra ? '  ' + extra : ''));
  if (!ok) fail++;
};

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다'); process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

/* 화면에 실제로 그려진 글자의 대비를 잰다. 팔레트만 보면 «토큰은 맞는데
   화면은 안 읽히는» 자리를 놓친다 — 색을 박아 둔 규칙이 토큰을 덮기 때문이다.
   그래서 **글자마다 제 색과 뒤에 깔린 색을 찾아** 비율을 낸다. */
const MEASURE = `(() => {
  const lum = (c) => {
    const [r,g,b] = c;
    const f = (v) => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b);
  };
  const parse = (s) => {
    const m = String(s||'').match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return { c:[p[0],p[1],p[2]], a: p.length > 3 ? p[3] : 1 };
  };
  /* 뒤에 깔린 색 — 투명한 조상을 타고 올라가 처음 만나는 불투명 바탕. */
  const behind = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const b = parse(getComputedStyle(e).backgroundColor);
      if (b && b.a >= 0.95) return b.c;
      if (b && b.a > 0) {           // 반투명이면 그 위에 얹어 섞는다
        const under = behind(e.parentElement) || [255,255,255];
        return b.c.map((v,i) => Math.round(v*b.a + under[i]*(1-b.a)));
      }
    }
    return [255,255,255];
  };
  const out = [];
  document.querySelectorAll('body *').forEach(el => {
    if (el.offsetParent === null && el.tagName !== 'BODY') return;   // 안 보이는 것
    const txt = [].filter.call(el.childNodes, n => n.nodeType === 3)
      .map(n => n.textContent.trim()).join('');
    if (!txt) return;                                                // 제 글자가 없는 상자
    const st = getComputedStyle(el);
    const fg = parse(st.color); if (!fg || fg.a < 0.5) return;
    const bg = behind(el);
    const L1 = lum(fg.c), L2 = lum(bg);
    const ratio = (Math.max(L1,L2) + 0.05) / (Math.min(L1,L2) + 0.05);
    const px = parseFloat(st.fontSize), bold = (parseInt(st.fontWeight,10) || 400) >= 700;
    const big = px >= 24 || (px >= 18.66 && bold);
    const need = big ? 3 : 4.5;
    if (ratio + 0.05 < need) {
      out.push({ t: txt.slice(0,22), r: Math.round(ratio*100)/100, need: need,
                 px: Math.round(px*10)/10, sel: el.tagName.toLowerCase() +
                 (el.className && typeof el.className === 'string'
                   ? '.' + el.className.split(' ')[0] : '') });
    }
  });
  return out;
})()`;

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  await noSheet(browser);

  const open = async (scheme) => {
    const ctx = await browser.newContext({ viewport: { width: 1100, height: 900 },
      colorScheme: scheme });
    const p = await ctx.newPage();
    await p.goto(`http://localhost:${PORT}/hub.html`,
      { waitUntil: 'domcontentloaded', timeout: 40000 });
    if (await p.$('#gateIn')) { await p.fill('#gateIn', '0000'); await p.click('#gateGo'); }
    await p.waitForFunction(() => !!document.getElementById('thmBtn'), null, { timeout: 30000 });
    await p.waitForTimeout(1200);
    return { ctx, p };
  };

  /* ── ① 기계가 어두우면 저절로 어두워진다 ── */
  console.log('── 기계 설정을 따른다 ──');
  {
    const { ctx, p } = await open('dark');
    const t = await p.evaluate(() => ({
      attr: document.documentElement.getAttribute('data-theme'),
      bg: getComputedStyle(document.body).backgroundColor,
      ink: getComputedStyle(document.documentElement).getPropertyValue('--ink').trim(),
      btn: (document.getElementById('thmBtn') || {}).textContent,
    }));
    /* 아무것도 안 골랐으니 표시는 안 붙는다 — 기계 설정을 그대로 따른다. */
    chk('안 골랐으면 표시가 안 붙는다', t.attr === null, String(t.attr));
    chk('그래도 어두워진다', /^rgb\(2[0-9], 2[0-9], 2[0-9]\)$/.test(t.bg) || t.ink === '#EAE8E1',
      t.bg + ' · --ink ' + t.ink);
    chk('단추가 «기계» 라고 말한다', /기계/.test(t.btn || ''), (t.btn || '').trim());
    await ctx.close();
  }

  /* ── ② 기계가 밝으면 밝다 (있던 화면을 안 건드린다) ── */
  console.log('\n── 밝은 옷은 그대로다 ──');
  {
    const { ctx, p } = await open('light');
    const t = await p.evaluate(() => ({
      bg: getComputedStyle(document.body).backgroundColor,
      ink: getComputedStyle(document.documentElement).getPropertyValue('--ink').trim(),
    }));
    chk('밝은 종이 그대로', t.ink === '#23201b', t.bg + ' · --ink ' + t.ink);
    await ctx.close();
  }

  /* ── ③ 고른 것이 기계보다 세다 · 다음에도 남는다 ── */
  console.log('\n── 고른 것이 이긴다 ──');
  {
    const { ctx, p } = await open('dark');
    /* 기계는 어둡다. 사람이 «밝게» 를 고르면 밝아야 한다. */
    await p.click('#thmBtn');                       // 기계 → 밝게
    await p.waitForTimeout(200);
    const light = await p.evaluate(() => ({
      attr: document.documentElement.getAttribute('data-theme'),
      ink: getComputedStyle(document.documentElement).getPropertyValue('--ink').trim(),
    }));
    chk('기계가 어두워도 «밝게» 면 밝다', light.attr === 'light' && light.ink === '#23201b',
      light.attr + ' · ' + light.ink);
    await p.click('#thmBtn');                       // 밝게 → 어둡게
    await p.waitForTimeout(200);
    const dark = await p.evaluate(() =>
      document.documentElement.getAttribute('data-theme'));
    chk('한 번 더 누르면 어둡게', dark === 'dark', String(dark));
    await p.reload({ waitUntil: 'domcontentloaded' });
    if (await p.$('#gateIn')) { await p.fill('#gateIn', '0000'); await p.click('#gateGo'); }
    await p.waitForFunction(() => !!document.getElementById('thmBtn'), null, { timeout: 20000 });
    const kept = await p.evaluate(() => ({
      attr: document.documentElement.getAttribute('data-theme'),
      btn: (document.getElementById('thmBtn') || {}).textContent,
    }));
    chk('새로고침해도 남는다', kept.attr === 'dark', String(kept.attr));
    chk('단추가 지금 옷을 말한다', /어둡게/.test(kept.btn || ''), (kept.btn || '').trim());
    await ctx.close();
  }

  /* ── ④ 어두운 옷에서 **실제로 읽히는가** ── */
  console.log('\n── 글자마다 진짜 대비를 잰다 ──');
  for (const tab of ['dash', 'stu', 'cls', 'rnd', 'con']) {
    const { ctx, p } = await open('dark');
    await p.evaluate(t => { try { show(t); } catch (e) {} }, tab);
    await p.waitForTimeout(900);
    const bad = await p.evaluate(MEASURE);
    chk(tab + ' 탭 — 안 읽히는 글자가 없다', bad.length === 0,
      bad.length ? bad.slice(0, 4).map(b =>
        `«${b.t}» ${b.r}:1 (${b.need} 필요 · ${b.px}px · ${b.sel})`).join(' / ')
        : '전부 통과');
    await ctx.close();
  }

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건` : '\n밤에도 읽힌다 — 자로 재서 그렇다.');
  process.exit(fail ? 1 : 0);
})();
