/* ============================================================
   **한 숫자는 한 자리에** — 허브 첫 화면 (브라우저 필요)
   ------------------------------------------------------------
   2026-08-14, 선생님 말씀 — *"hub에 3D 반 돌아가는건 의미가 없는거같아
   맥거핀이야. 빼줘. 의미있는걸로 허브를 재설계해야해."*

   재어 보니 3D 가 나빠서가 아니었다. 「미응시 4」 라는 **한 숫자가 화면에
   여섯 번** 나오고 있었다 — 위 카드 · 「오늘 할 일」 한 줄 · 바로가기 칩 줄 ·
   도넛과 막대 · 3D 탑 · 그리고 이름이 다 적힌 목록. 3D 는 그중 다섯째
   사본이었고, 하필 **읽을 수도 누를 수도 없는** 모양이었다.

   여기서 지키는 것
   ----------------
     · 3D 가 **한 조각도 안 남는다** — 캔버스도, 그리는 코드도
     · 같은 숫자를 **두 줄 잇달아 적지 않는다**(「오늘 할 일」 과 칩 줄이 그랬다)
     · 반별 현황은 **읽을 수 있고 누를 수 있다** — 3D 가 혼자 하던 일이다
     · 미응시 숫자를 누르면 **그 반 줄**로 간다(목록이 반별로 묶여 있다)
     · 급한 칸과 흐름 숫자가 **같은 무게로 서지 않는다**
     · 흐름 숫자는 **하나도 안 사라진다** — 자리만 옮겼지 지운 게 아니다

   ⚠ 이 검사는 «보기 좋은가» 를 안 본다. 그건 사람이 본다. 여기서 보는 것은
     **같은 것을 두 번 말하지 않는가**와 **누르면 갈 데가 있는가**다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/hub-dash.js
   ============================================================ */
'use strict';
const path = require('path');
const fs = require('fs');
const { serve } = require('./_serve.js');

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

/* 반 셋 · 학생 열둘. 미응시·재시·통과가 **반마다 다르게** 나오도록 심는다 —
   다 같으면 «급한 순으로 세운다» 를 잴 수가 없다. */
const NM = ['강신우', '고영훈', '김도윤', '김서준', '박하준', '이서연',
            '정민재', '최유진', '한지호', '오세훈', '윤채원', '임태균'];
const CLASSES = [
  { label: '화학1 목6-10', course: 'ch1', round: 7,
    students: NM.slice(0, 8).map(n => ({ name: n, school: '휘문중', year: '2' })) },
  { label: '화학2 토2-6', course: 'ch2', round: 5,
    students: NM.slice(4, 12).map(n => ({ name: n, school: '대청중', year: '3' })) },
  { label: '일반화학 수7-9', course: 'gc', round: 3,
    students: NM.slice(2, 7).map(n => ({ name: n, school: '단대부중', year: '2' })) },
];
const SHEET = {
  ok: true, classes: CLASSES, rows: [], students: [], list: [], mis: [],
  views: [], sent: [], snoozed: [], changed: 0,
  passed: [{ name: '김도윤', school: '휘문중', course: 'ch1', round: 7 },
           { name: '박하준', school: '휘문중', course: 'ch1', round: 7 },
           { name: '이서연', school: '대청중', course: 'ch2', round: 5 }],
  pending: [{ name: '강신우', school: '휘문중', course: 'ch1', round: 7, score: 62 },
            { name: '정민재', school: '대청중', course: 'ch2', round: 5, score: 71 },
            { name: '한지호', school: '대청중', course: 'ch2', round: 5, score: 58 },
            { name: '윤채원', school: '대청중', course: 'ch2', round: 5, score: 66 }],
  absentees: { classes: [
    { label: '화학1 목6-10', course: 'ch1', round: 7, absent: ['고영훈', '김서준', '최유진'], total: 8 },
    { label: '일반화학 수7-9', course: 'gc', round: 3, absent: ['오세훈'], total: 5 }] },
};

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  /* NOSHEET-예외: 이 검사는 **화면에 자료를 먹여 놓고** 보는 것이라
     `_nosheet` 로 덮으면(빈 답) 반별 현황도 목록도 안 그려져 잴 것이 없다.
     대신 script.google* 를 통째로 가로채 **내가 지은 답**만 준다 — 가로챈
     요청은 망으로 안 나가므로 진짜 시트에는 한 글자도 안 닿는다.
     (`tools/test_nosheet.py` 가 이 표시와 실제로 막는 자리를 같이 본다) */
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('**://script.google*.com/**', r => {
    const u = new URL(r.request().url());
    const cb = u.searchParams.get('callback');
    const want = (u.searchParams.get('want') || '').split(',').filter(Boolean);
    const parts = {}; want.forEach(w => { parts[w] = SHEET; });
    const body = JSON.stringify(Object.assign({}, SHEET, { parts: parts }));
    return r.fulfill({ status: 200, contentType: cb ? 'text/javascript' : 'application/json',
      body: cb ? cb + '(' + body + ');' : body });
  });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 110)));
  await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded', timeout: 40000 });
  if (await p.$('#gateIn')) { await p.fill('#gateIn', '0000'); await p.click('#gateGo'); }
  await p.waitForFunction(() => !!document.querySelector('.clsrow__r'), null, { timeout: 30000 });

  /* ── ① 3D 가 한 조각도 안 남았다 ── */
  console.log('── 3D 를 걷어냈다 ──');
  const left = await p.evaluate(() => ({
    canvas: document.querySelectorAll('canvas').length,
    ids: ['hero3d', 'tw3d', 'tw3dTags', 'dash3d'].filter(x => !!document.getElementById(x)),
    fns: ['G3', 'TOWER_FS', 'HERO_FS', 'heroStart', 'heroRefresh', 'renderTowers']
      .filter(n => typeof window[n] !== 'undefined'),
  }));
  chk('캔버스가 하나도 없다', left.canvas === 0, left.canvas + '개');
  chk('3D 자리표가 안 남았다', left.ids.length === 0, left.ids.join(' ') || '없음');
  chk('3D 코드가 안 남았다', left.fns.length === 0, left.fns.join(' ') || '없음');
  const src = fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8');
  chk('셰이더 글자가 파일에 안 남았다',
    !/gl_FragColor|createShader|getContext\(['"]webgl/.test(src));

  /* ── ② 같은 숫자를 두 줄 잇달아 적지 않는다 ── */
  console.log('\n── 한 숫자는 한 자리에 ──');
  const dup = await p.evaluate(() => {
    /* 「오늘 할 일」 과 그 아래 칩 줄이 글자까지 같았다. 첫 화면에서 «시험
       미응시» 라는 말이 몇 번 나오는지 센다(제목·설명문은 뺀다). */
    const chips = [].map.call(document.querySelectorAll('#todo .chip, .chips .chip'),
      c => c.textContent.replace(/\s+/g, ' ').trim());
    const seen = {}; let same = 0;
    chips.forEach(t => { if (seen[t]) same++; seen[t] = 1; });
    return { chips: chips, same: same, jumpRow: !!document.getElementById('jump') };
  });
  chk('겹친 칩 줄이 없어졌다', dup.jumpRow === false);
  chk('같은 칩이 두 번 안 선다', dup.same === 0,
    dup.same ? '겹친 것 ' + dup.same + '개' : dup.chips.join(' / '));

  /* ── ③ 흐름 숫자는 하나도 안 사라졌다 ── */
  const flow = await p.evaluate(() => {
    const ids = ['todayCnt', 'weekCnt', 'finStuCnt', 'finRecCnt', 'finRndCnt'];
    const miss = ids.filter(i => !document.getElementById(i));
    const line = document.querySelector('.flowline');
    const cards = document.querySelectorAll('#dashCards .card').length;
    return { miss: miss, inLine: !!line && ids.every(i => line.contains(document.getElementById(i))),
             cards: cards };
  });
  chk('흐름 숫자 다섯이 다 있다', flow.miss.length === 0, flow.miss.join(' ') || '5개 다 있음');
  chk('흐름은 한 줄에 눕는다', flow.inLine === true);
  /* 급한 칸만 카드로 선다 — 여덟이면 급한 것이 안 급해 보인다. */
  chk('카드는 급한 셋뿐이다', flow.cards === 3, flow.cards + '칸');

  /* ── ④ 반별 현황: 읽을 수 있고 누를 수 있다 ── */
  console.log('\n── 반별 현황 (3D 탑이 하던 일) ──');
  const row = await p.evaluate(() => {
    const rs = [].map.call(document.querySelectorAll('.clsrow__r'), r => ({
      t: r.textContent.replace(/\s+/g, ' ').trim(),
      miss: Number((r.querySelector('.clsrow__n.bad') || {}).textContent || 0),
      wait: Number((r.querySelector('.clsrow__n.warn') || {}).textContent || 0),
    }));
    return { rows: rs, n: rs.length };
  });
  chk('반마다 한 줄씩 선다', row.n === 3, row.n + '줄');
  chk('반 이름이 글자로 읽힌다', row.rows.every(r => /[가-힣]/.test(r.t)),
    row.rows.map(r => r.t.slice(0, 12)).join(' / '));
  /* 급한 순 — 이름 순으로 두면 여덟 줄을 눈으로 훑어야 한다. */
  const urg = row.rows.map(r => r.miss + r.wait);
  chk('급한 순으로 선다', urg.every((v, i) => i === 0 || urg[i - 1] >= v), urg.join(' ≥ '));

  /* ── ⑤ 누르면 그 반 줄로 간다 ── */
  console.log('\n── 눌러서 이름까지 ──');
  const go = await p.evaluate(async () => {
    const r = [].slice.call(document.querySelectorAll('.clsrow__r'))
      .find(x => /화학1/.test(x.textContent));
    const b = r && r.querySelector('.clsrow__n.bad');
    if (!b) return { no: '미응시 단추가 없다' };
    const to = b.dataset.jump;
    b.click();
    await new Promise(z => setTimeout(z, 900));
    const t = document.getElementById(to);
    return { to: to, exists: !!t,
             text: t ? t.textContent.replace(/\s+/g, ' ').trim() : '',
             top: t ? Math.round(t.getBoundingClientRect().top) : null,
             vh: window.innerHeight };
  });
  chk('미응시는 **그 반 줄**로 간다', /^absC\d+$/.test(go.to || ''), go.to || go.no);
  chk('그 자리가 실제로 있다', go.exists === true);
  chk('그 반 이름이 거기 있다', /화학1/.test(go.text || ''), (go.text || '').slice(0, 26));
  chk('화면 안으로 들어온다', go.top != null && go.top >= 0 && go.top < go.vh,
    go.top + 'px (창 ' + go.vh + ')');

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n한 숫자는 한 자리에 있고, 누르면 이름까지 간다.');
  process.exit(fail ? 1 : 0);
})();
