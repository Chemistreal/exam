/* ============================================================
   3D 가 화면을 망가뜨리지 않았는가
   ------------------------------------------------------------
   그림은 재기 어렵다. "좀 화려한가?" 로는 아무것도 확인이 안 된다.
   그래서 잴 수 있는 것만, 대신 **진짜 화소를 읽어** 잰다.

   1) 글씨가 그림에 먹히지 않았는가.
      띠 안의 글자마다 **그 글자가 실제로 앉은 자리**의 캔버스 화소를 읽어
      대비를 계산한다. CSS 변수를 재는 것이 아니다 — 셰이더는 CSS 에 안
      걸리므로, 팔레트만 재면 그림이 아무리 밝아도 초록불이 나온다.
   2) 그림이 **유일한 통로**가 아닌가. 낭독기에 낱말 요약이 가는가.
   3) WebGL 이 없는 기기에서 **빈 구멍**이 남지 않는가.
   4) 안 보일 때 프레임을 멈추는가 — 대시보드를 켜 놓고 수업하는 화면이다.
      멈추지 않으면 노트북이 하루 종일 돈다.
   5) 움직임 줄이기를 켜면 **도는 것만** 멈추는가(3D 는 남아야 한다).

   실행:
       NODE_PATH=tests/node_modules node tests/hero3d.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(300);
const seal = require('./_seal.js');
const { spawn } = require('child_process');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8937);
const ROOT = path.join(__dirname, '..');
const DT_EP = 'AKfycbzvFaPXgEgCBQ8HowtP8tPTtdiIVFtmZSUf0KFXUOVOh3ektrFMkz4KSR4I52LDBzB8rw';

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

/* 반이 여럿이어야 탑이 여럿 선다. 한 반만 두면 '여러 반' 쪽 길이 안 걸린다. */
function part(a) {
  const S = (n, sc, y) => ({ name: n, school: sc, year: y });
  const map = {
    names: { ok: true, classes: [
      { label: '화학1 일6-10', course: 'ch1', kind: 'dt',
        students: [S('강신우', '대치중', '2'), S('고영훈', '대신중', '1'),
                   S('김도윤', '휘문중', '2')] },
      { label: '화학1 수6-10', course: 'ch1b', kind: 'dt',
        students: [S('박서준', '단대부중', '3'), S('이하은', '대명중', '2')] },
      { label: '파이널 목7-10', course: '', kind: 'exam',
        students: [S('박하람', '대청중', '3')] } ] },
    pending: { ok: true, pending: { active: [
      { name: '강신우', course: 'ch1', round: 12, lastAttempt: '정시',
        nextNeeded: '재시', score: 62, days: 5, studentKey: 's1' } ] } },
    passed: { ok: true, passed: { passed: [
      { name: '고영훈', course: 'ch1', round: 12, attempt: '정시',
        tries: 1, score: 96, date: '8/1', days: 2 },
      { name: '이하은', course: 'ch1b', round: 12, attempt: '정시',
        tries: 1, score: 91, date: '8/1', days: 2 } ] } },
    absentees: { ok: true, absentees: { classes: [
      { label: '화학1 일6-10', course: 'ch1', round: 12, total: 3, present: 2,
        absent: ['김도윤'] } ] } },
    cohortmis: { ok: true, rows: [] },
    sentlog: { ok: true, sent: [] }, snoozelog: { ok: true, snoozed: [] },
    views: { ok: true, views: [] }, mistags: { ok: true, mis: { rows: [] } },
  };
  return map[a] || { ok: true };
}

async function open(browser, opt) {
  const ctx = await browser.newContext(Object.assign(
    { viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' }, opt || {}));
  const p = await ctx.newPage();
  p.__errs = [];
  p.on('pageerror', e => p.__errs.push(String(e).slice(0, 140)));
  await p.addInitScript(() => {
    try {
      localStorage.setItem('chemistreal:gate', String(Date.now()));
      /* 띠의 사슬은 **채점한 회차**를 나른다. 자료가 없으면 그릴 것이 없어
         빈 띠가 맞는 동작이라, 검사에서는 회차를 심어 준다. 회차마다 인원과
         평균이 달라야 크기·색이 자료를 싣는지 볼 수 있다. */
      const seed = (id, people) => {
        const day = 86400000, base = 1785000000000;
        localStorage.setItem('final:roster:' + id, JSON.stringify(people.map((x, i) => ({
          name: x[0], school: 'X중', grade: '3', ts: base + i * day,
          correct: x[1], total: 60, wrong: 60 - x[1], ans: [],
        }))));
      };
      seed('jmchc-9',  [['가온', 52], ['나린', 48], ['다솔', 44]]);        // 평균 높다
      seed('jmchc-10', [['가온', 33], ['나린', 30]]);                      // 중간
      seed('jmchc-11', [['가온', 18], ['나린', 20], ['다솔', 22], ['라온', 19]]); // 낮다
    } catch (e) {}
  });
  await p.route('**/DT/**', r => r.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8">' }));
  await p.route('**/macros/s/**', r => {
    const u = new URL(r.request().url()), cb = u.searchParams.get('callback') || 'cb';
    const isDT = u.pathname.includes(DT_EP), a = u.searchParams.get('action');
    let body;
    if (isDT && a === 'bundle') {
      const ps = {};
      String(u.searchParams.get('want') || '').split(',').filter(Boolean)
        .forEach(x => { ps[x] = part(x); });
      body = { ok: true, bundle: true, parts: ps };
    } else if (isDT) body = part(a);
    else body = { ok: true, students: [] };
    return r.fulfill({ status: 200, contentType: 'text/javascript',
      body: cb + '(' + JSON.stringify(body) + ');' });
  });
  return p;
}

/* 글자가 실제로 앉은 자리의 화소를 읽어 최악의 대비를 낸다.

   ⚠ WebGL 캔버스에서 readPixels 로 읽으면 **빈 그림이 나온다.** 화면에 합친
     뒤 브라우저가 그리기 통을 비우기 때문이다(preserveDrawingBuffer 를 켜면
     되지만, 그건 매 프레임 통을 하나 더 들고 있으라는 뜻이라 실물이 느려진다
     — 검사 때문에 실물을 느리게 하지 않는다).
     그래서 **띠를 사진으로 찍어** 읽는다. 합쳐진 결과를 그대로 재는 것이라
     알파 합성을 손으로 계산할 일도 없다 — 더 정확하다.
   ⚠ 찍기 전에 글자만 투명하게 만든다. 안 그러면 글자 획이 같이 찍혀서
     '바탕' 이 아니라 글자색을 재게 된다. 깔개(배경)는 그대로 남는다. */
async function measureBrand(p) {
  const nodes = await p.evaluate(() => {
    const bb = document.querySelector('.brand').getBoundingClientRect();
    const out = [];
    document.querySelectorAll('.brand h1, .brand .sub').forEach(el => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      const cs = getComputedStyle(el);
      const size = parseFloat(cs.fontSize);
      out.push({
        who: el.id || el.className || el.tagName.toLowerCase(),
        x: r.left - bb.left, y: r.top - bb.top, w: r.width, h: r.height,
        fg: cs.color,
        /* 24px 이상 또는 18.66px 굵은 글씨는 큰 글씨(3:1), 나머지는 본문(4.5:1) */
        need: (size >= 24 || (size >= 18.66 && Number(cs.fontWeight) >= 700)) ? 3 : 4.5,
      });
    });
    return out;
  });
  await p.addStyleTag({ content:
    '.brand h1,.brand .sub{color:transparent !important;text-shadow:none !important}' });
  await p.waitForTimeout(350);
  const png = (await p.locator('.brand').screenshot()).toString('base64');
  return p.evaluate(async ({ png, nodes }) => {
    const bmp = await createImageBitmap(await (await fetch('data:image/png;base64,' + png)).blob());
    const cv = document.createElement('canvas');
    cv.width = bmp.width; cv.height = bmp.height;
    const g = cv.getContext('2d');
    g.drawImage(bmp, 0, 0);
    const px = g.getImageData(0, 0, cv.width, cv.height).data;
    const at = (x, y) => {
      const i = (Math.min(cv.height - 1, Math.max(0, Math.round(y))) * cv.width +
                 Math.min(cv.width - 1, Math.max(0, Math.round(x)))) * 4;
      return [px[i], px[i + 1], px[i + 2]];
    };
    const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    const L = q => 0.2126 * f(q[0]) + 0.7152 * f(q[1]) + 0.0722 * f(q[2]);
    const parse = s => { const m = /rgba?\(([^)]+)\)/.exec(s || '');
      const a = m[1].split(/[,\s/]+/).map(Number); return [a[0], a[1], a[2]]; };

    const rows = nodes.map(nd => {
      const fg = parse(nd.fg), lf = L(fg);
      let worst = 99, bg = null;
      /* 한 점만 재면 제일 밝은 화소를 놓친다 — 상자 안을 격자로 훑는다. */
      for (let gy = 0; gy <= 8; gy++) for (let gx = 0; gx <= 20; gx++) {
        const q = at(nd.x + nd.w * (gx / 20), nd.y + nd.h * (gy / 8));
        const lb = L(q);
        const c = (Math.max(lf, lb) + 0.05) / (Math.min(lf, lb) + 0.05);
        if (c < worst) { worst = c; bg = q; }
      }
      return { who: nd.who, r: Math.round(worst * 100) / 100, need: nd.need, bg: bg };
    });

    /* 그림이 실제로 그려졌는가 — 왼쪽 끝(가려 둔 자리)의 색과 다른 화소를 센다.
       셰이더가 통째로 안 돌았는데도 초록불이 나오는 것을 막는다. */
    const base = at(2, cv.height / 2);
    let ink = 0;
    for (let x = Math.round(cv.width * 0.65); x < cv.width - 2; x += 3)
      for (let y = 2; y < cv.height - 2; y += 3) {
        const q = at(x, y);
        if (Math.abs(q[0]-base[0]) + Math.abs(q[1]-base[1]) + Math.abs(q[2]-base[2]) > 12) ink++;
      }
    /* 프레임이 바뀌었는지 보려고 그림 전체를 한 숫자로 줄여 둔다. */
    let sig = 0;
    for (let i = 0; i < px.length; i += 401) sig = (sig * 31 + px[i]) % 2147483647;
    return { rows: rows, ink: ink, sig: sig };
  }, { png: png, nodes: nodes });
}

(async () => {
  const srv = spawn(process.execPath, ['-e', `
    const http=require('http'),fs=require('fs'),p=require('path');
    const T={'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.css':'text/css'};
    http.createServer((q,s)=>{
      const f=p.join(${JSON.stringify(ROOT)}, decodeURIComponent(q.url.split('?')[0]));
      fs.readFile(f,(e,d)=>e?(s.writeHead(404),s.end()):(s.writeHead(200,{'Content-Type':T[p.extname(f)]||'text/plain'}),s.end(d)));
    }).listen(${PORT});
  `], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 700));
  const URL_ = `http://localhost:${PORT}/hub.html`;

  const browser = seal(await chromium.launch(Object.assign(
    { args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {})));

  try {
    console.log('── ① 그림 위의 글씨 ──');
    {
      const p = await open(browser);
      await p.goto(URL_, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(3000);
      const m = await measureBrand(p);
      console.log(`  띠에서 그림이 닿은 화소 ${m.ink}개`);
      chk('띠 안에 분자가 실제로 그려졌다', m.ink > 200, true);
      m.rows.forEach(row => {
        console.log(`  ${row.who} — ${row.r}:1 (기준 ${row.need}) 바탕 rgb(${(row.bg || []).join(',')})`);
        chk('그림 위에서도 읽힌다 · ' + row.who, row.r >= row.need, true);
      });
      /* 한 마디도 안 재고 통과하는 것을 막는다. */
      chk('띠 안의 글자를 빼놓지 않고 쟀다', m.rows.length >= 3, true);
      chk('콘솔에 예외가 없다', p.__errs, []);
      await p.context().close();
    }

    console.log('\n── ② 그림이 유일한 통로가 아니다 ──');
    {
      const p = await open(browser);
      await p.goto(URL_, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(3000);
      const r = await p.evaluate(() => {
        const cv = document.getElementById('tw3d');
        return { has: !!cv,
                 label: cv ? (cv.getAttribute('aria-label') || '') : '',
                 role: cv ? cv.getAttribute('role') : '',
                 tab: cv ? cv.getAttribute('tabindex') : null,
                 /* 이름표는 그림 위에 떠 있다 — 보이는 것만 센다.
                    겹쳐서 감춘 것은 자리가 없다는 뜻이라 세지 않는다. */
                 names: [...document.querySelectorAll('#tw3dTags span')]
                   .filter(e => Number(e.style.opacity || 1) > 0.1).length,
                 /* 그림을 다 지워도 같은 내용이 글로 남는가 */
                 text: !!document.getElementById('dashFig').textContent.trim() };
      });
      chk('반별 탑이 섰다', r.has, true);
      console.log('  낱말 요약: ' + r.label.slice(0, 90) + '…');
      chk('낱말 요약에 반 이름과 숫자가 들어 있다',
          /명\(미응시 \d+ · 재시 \d+ · 통과 \d+\)/.test(r.label), true);
      chk('낭독기에 그림이라고 알린다', r.role, 'img');
      chk('키보드로도 닿는다', r.tab, '0');
      chk('탑 밑에 반 이름이 적혀 있다', r.names > 0, true);
      chk('같은 내용이 글로도 있다', r.text, true);

      /* ── 띠도 자료를 나른다 ──────────────────────────────────────
         "모든 형태는 기능을 따른다." 띠 안의 사슬은 오래 **지어낸 모양**
         이었다 — sin() 으로 만든 무한 사슬이라 아무 말도 안 했다. 지금은
         구슬 하나가 회차 하나다. 그러니 낱말 요약도 있어야 한다. */
      const hb = await p.evaluate(() => {
        const cv = document.getElementById('hero3d');
        if (!cv) return { has: false };
        return { has: true, role: cv.getAttribute('role'),
                 label: cv.getAttribute('aria-label') || '',
                 hidden: cv.getAttribute('aria-hidden'),
                 title: cv.title || '',
                 /* 자료가 진짜로 셰이더까지 갔는가 — 회차 수가 0 이면 안 된다.
                    `let HERO` 는 window 의 값이 아니다 — 이름 그대로 봐야 보인다. */
                 n: (typeof HERO !== 'undefined' && HERO) ? HERO.n : 0,
                 /* 반지름이 다 같으면 인원을 안 싣고 있다는 뜻이다 */
                 radii: (typeof HERO !== 'undefined' && HERO && HERO.A)
                   ? [...Array(HERO.n)].map((_, i) => Math.round(HERO.A[i * 4 + 2] * 1000)) : [] };
      });
      chk('띠에 사슬이 있다', hb.has, true);
      console.log('  띠 요약: ' + hb.label.slice(0, 90) + '…');
      chk('회차를 싣고 있다', hb.n > 0, true);
      chk('낭독기에 그림이라고 알린다 · 띠', hb.role, 'img');
      chk('감춰 두지 않는다 · 띠', hb.hidden, null);
      chk('낱말 요약이 무엇을 뜻하는지 말한다',
          /구슬 크기는 본 학생 수/.test(hb.label) && /평균 성취/.test(hb.label), true);
      chk('회차 이름과 숫자가 들어 있다', /\d+명 평균 \d+%/.test(hb.label), true);
      chk('마우스를 얹어도 같은 말이 나온다', hb.title.length > 20, true);
      /* 회차마다 인원이 다르면 구슬 크기도 달라야 한다. 다 같으면 크기가
         자료를 안 싣고 있는 것이다 — 그때가 '모양만 남은' 상태다. */
      chk('인원이 크기로 실렸다',
          hb.radii.length < 2 || new Set(hb.radii).size > 1, true);

      chk('콘솔에 예외가 없다', p.__errs, []);
      await p.context().close();
    }

    console.log('\n── ③ WebGL 이 없는 기기 ──');
    {
      const p = await open(browser);
      await p.addInitScript(() => {
        /* 옛 기기·꺼 둔 기기에서 실제로 이렇게 된다. */
        const g = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (t) {
          /* 'experimental-webgl' 도 막는다. 이것만 빼놓으면 크롬이 진짜
             맥락을 돌려줘서, 검사는 'WebGL 없는 기기' 를 재고 있다고 믿지만
             실제로는 있는 기기를 재고 있다. */
          if (/webgl/i.test(String(t))) return null;
          return g.apply(this, arguments);
        };
      });
      await p.goto(URL_, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(2500);
      const r = await p.evaluate(() => ({
        hero: !!document.getElementById('hero3d'),
        hole: !!document.querySelector('#dash3d canvas'),
        alive: !!document.querySelector('#dashCards .card'),
        fig: !!document.getElementById('dashFig').textContent.trim(),
      }));
      chk('화면이 산다', r.alive, true);
      chk('빈 캔버스를 안 남긴다 · 띠', r.hero, false);
      chk('빈 캔버스를 안 남긴다 · 반별 탑', r.hole, false);
      chk('글자 그림은 그대로 있다', r.fig, true);
      chk('콘솔에 예외가 없다', p.__errs, []);
      await p.context().close();
    }

    console.log('\n── ④ 안 보이면 안 그린다 ──');
    {
      const p = await open(browser);
      await p.addInitScript(() => {
        window.__raf = 0;
        const raf = window.requestAnimationFrame;
        window.requestAnimationFrame = function (f) { window.__raf++; return raf.call(window, f); };
      });
      await p.goto(URL_, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(2500);
      /* ⚠ '저절로 도는가' 로 재지 않는다. 검사판에는 그래픽 카드가 없어
         화면이 **일부러 정지화면으로** 남기 때문이다 — 그렇게 재면 여기서
         늘 0이 나와서, 멈춤 장치가 고장 나도 초록불이 뜬다.
         대신 **다시 그릴 일을 만들어** 그때 도는지 본다. */
      const poke = () => p.evaluate(() => new Promise(res => {
        const a = window.__raf;
        window.dispatchEvent(new Event('resize'));
        setTimeout(() => res(window.__raf - a), 600);
      }));
      const live = await poke();
      chk('보일 때는 다시 그린다', live > 0, true);
      await p.evaluate(() => {
        Object.defineProperty(document, 'hidden', { get: () => true, configurable: true });
        Object.defineProperty(document, 'visibilityState',
          { get: () => 'hidden', configurable: true });
        document.dispatchEvent(new Event('visibilitychange'));
      });
      await p.waitForTimeout(500);
      const idle = await poke();
      console.log(`  보일 때 ${live}프레임 → 숨었을 때 ${idle}프레임`);
      chk('탭이 뒤에 있으면 멈춘다', idle, 0);
      await p.context().close();
    }

    console.log('\n── ⑤ 움직임 줄이기 ──');
    {
      const p = await open(browser, { reducedMotion: 'reduce' });
      await p.goto(URL_, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(2500);
      const a = await measureBrand(p);
      await p.waitForTimeout(1200);
      const b = await measureBrand(p);
      console.log(`  그림 화소 ${a.ink}개 · 그림 지문 ${a.sig} → ${b.sig}`);
      /* 3D 는 남고 **도는 것만** 멈춘다. 어지럼증 때문에 켜 둔 설정을
         그림 하나로 무시하지 않지만, 그렇다고 그림을 뺏지도 않는다. */
      chk('3D 는 그대로 그려진다', a.ink > 200, true);
      chk('돌지는 않는다', a.sig === b.sig, true);
      await p.context().close();
    }
  } finally {
    await browser.close();
    srv.kill();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
