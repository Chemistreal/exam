/* ============================================================
   약점 극복 60제 Word — 시험지에 답이 없고, 세 갈래 판정이 맞다

   세 문서가 나간다. 1교시 시험지, 2교시 되풀이, 그리고 해설이다.
   앞의 둘은 학생이 손에 들고 푸는 종이라서 **정답이 한 자라도 실리면 그
   자리에서 못 쓴다.** 눈으로는 못 본다 — 60문항이 스물몇 장이다.
   그래서 **찍어서 잰다.**

   되풀이 시험지에는 힌트가 세 층 붙는다. 그 힌트는 해설 본문에서 잘라 오는데,
   해설 본문은 「정답 ②」로 끝난다. 절을 하나 잘못 집으면 그대로 답이 실린다 —
   이 검사가 막는 것이 바로 그것이다.

   머리(번호·영역)와 문항 그림도 갈라지면 안 된다. 처음에는 둘을 따로 문단으로
   두고 keepNext 만 걸었는데, LibreOffice 로 찍어 보니 스물다섯 쪽 가운데
   **열여섯 쪽**에서 머리만 쪽 끝에 남고 그림은 다음 장으로 갔다. 지금은 한
   문단에 넣어 어느 뷰어에서도 갈라지지 않게 해 두었다 — 그 성질을 여기서 지킨다.

   그리고 **세 갈래 판정**을 잰다. 1교시에 맞았으면 「안다」, 1교시엔 틀리고
   2교시엔 맞았으면 「알지만 못 꺼낸다」, 두 번 다 틀렸으면 「모른다」다.
   같은 오답이라도 처방이 정반대여서, 이 판정이 어긋나면 문서가 거짓말을 한다.
   화면이 셈한 값이 아니라 **찍힌 종이에 적힌 낱말**을 세어 견준다.

   ⚠ LibreOffice(writer)와 poppler(pdftotext·pdfimages)가 있어야 돈다.
     없으면 조용히 지나가지 않는다 — REQUIRE_SOFFICE 가 켜져 있으면 멈춘다.

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/weak60-docx.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(900);
const fs = require('fs'), path = require('path'), os = require('os');
const { execFileSync } = require('child_process');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);

function have(cmd, args) {
  try { execFileSync(cmd, args, { stdio: 'ignore', timeout: 120000 }); return true; }
  catch (e) { return false; }
}
function sofficeCanWrite() {
  const reg = ['/usr/lib/libreoffice/share/registry/writer.xcd',
               '/usr/lib64/libreoffice/share/registry/writer.xcd'];
  return have('soffice', ['--version']) && reg.some(p => fs.existsSync(p));
}

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) { console.log('실패: playwright 를 찾지 못했다'); process.exit(1); }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}
const noSheet = require('./_nosheet.js');
const seal = require('./_seal.js');

const OUT = path.join(os.tmpdir(), 'chemistreal-weak60');
let fail = 0;
const chk = (n, ok, info) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (ok ? '' : '   ' + info));
  if (!ok) fail++;
};
const pdf = f => execFileSync('pdftotext', ['-layout', f, '-'], { encoding: 'utf8', maxBuffer: 64 << 20 });

/* 60칸에 값을 넣고 화면이 알아채게 한다 — 손으로 치는 것과 같은 길로 간다. */
async function fillBoxes(p, sel, vals) {
  await p.evaluate(({ sel, vals }) => {
    const ins = document.querySelectorAll(sel + ' .cellbox input');
    ins.forEach((inp, i) => {
      inp.value = vals[i] ? String(vals[i]) : '';
      inp.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }, { sel, vals });
}

(async () => {
  if (!sofficeCanWrite() || !have('pdftotext', ['-v'])) {
    const msg = 'LibreOffice(writer) 또는 poppler 가 없다 — 장을 찍어 볼 수 없다';
    if (process.env.REQUIRE_SOFFICE) { console.log('실패: ' + msg); process.exit(1); }
    console.log('건너뜀: ' + msg); process.exit(0);
  }
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });

  const b = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  await noSheet(b);
  const ctx = await b.newContext({ acceptDownloads: true });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const got = [];
  p.on('download', async d => {
    const f = path.join(OUT, 'd' + got.length + '.docx');
    await d.saveAs(f); got.push({ file: f });
  });
  /* ⚠ 파일 이름은 `download.suggestedFilename()` 으로 못 잰다. 머리 없는
     크로뮴은 blob: 내려받기에서 <a download> 를 안 읽고 늘 'download' 를
     돌려준다(따로 찍어 확인). 선생님이 실제로 받는 이름은 앱이 _saveBlob
     에 넘기는 그 이름이므로, **그 자리**에서 잡는다. */
  const spy = async () => p.evaluate(() => {
    window.__names = [];
    const o = window._saveBlob;
    window._saveBlob = function (b, fn) { window.__names.push(fn); return o(b, fn); };
  });

  await p.goto(`http://localhost:${PORT}/weak60.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof EXAMS !== 'undefined' && EXAMS.length > 0, { timeout: 30000 });

  /* ── 기록이 없으면 그렇게 말한다 ───────────────────────
     없는 것을 있다고 하지 않는다. 빈 명단에 학생 이름이 지어져 나오면 안 된다. */
  /* ⚠ 이 화면에도 문고리가 걸려 있다(코드 0000). 덮개가 떠 있으면 단추를
       못 누른다. 검사는 이미 통과한 브라우저인 척한다 — 문고리 자체는
       tests/weak60-shared.js 가 따로 본다. */
  const GATE = 'chemistreal:gate';
  const empty = await p.evaluate((k) => {
    localStorage.clear(); localStorage.setItem(k, String(Date.now()));
    return { names: rosterNames().length, hist: histOf('없는사람').length };
  }, GATE);
  chk('채점 기록이 없으면 명단이 비어 있다', empty.names === 0 && empty.hist === 0, JSON.stringify(empty));

  /* ── 여러 회차를 푼 학생을 심는다 ──────────────────────
     회차마다 다른 간격으로 틀리게 해서 영역이 골고루 쌓이게 한다.
     5의 배수 자리는 무응답으로 둔다 — 찍어서 틀린 것과 손도 못 댄 것을
     함께 봐야 하기 때문이다. */
  const seeded = await p.evaluate((k) => {
    localStorage.clear(); localStorage.setItem(k, String(Date.now()));
    const ids = ['kmchc-2025-1-ilban', 'kmchc-2025-2-ilban', 'kmchc-2026-1-ilban', 'kmchc-2024-2']
      .filter(id => EXAMS.some(e => e.id === id));
    ids.forEach((id, k) => {
      const e = EXAMS.find(x => x.id === id);
      const ans = [];
      for (let q = 1; q <= e.nQ; q++) {
        const acc = (e.multi && e.multi[q]) || [e.key[q - 1]];
        const right = acc[0] || 1;
        const bad = (q % (4 + k)) === 1;
        ans.push(bad ? ((q % 5 === 0) ? 0 : ((right % 4) + 1)) : right);
      }
      let c = 0; for (let q = 1; q <= e.nQ; q++) if (okq(e, q, ans[q - 1])) c++;
      const cur = subs(id);
      cur.push({ name: '검사용', school: '대원국제중', grade: '3', ts: Date.now() - k * 86400000,
                 correct: c, total: e.nQ, wrong: e.nQ - c, ans });
      localStorage.setItem(PFX + cohortKey(id), JSON.stringify(cur));
    });
    return ids.length;
  }, GATE);
  chk('회차를 심었다', seeded >= 3, '심은 회차 ' + seeded);

  await p.reload({ waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof EXAMS !== 'undefined' && EXAMS.length > 0, { timeout: 30000 });
  await p.waitForTimeout(300);
  chk('문고리 덮개가 걷혔다', (await p.locator('#gate').count()) === 0, '');
  await spy();

  /* ── 배정이 영역으로 나뉘고, 되풀이 오답이 앞선다 ────── */
  const plan = await p.evaluate(async () => {
    const rows = weakScan('검사용');
    const areas = weakAreas(rows), types = weakTypes(rows);
    const items = await weak60Fill(weak60Plan(areas, 60, {}));
    const byArea = {}; items.forEach(it => { byArea[it.area] = (byArea[it.area] || 0) + 1; });
    const kinds = {}; items.forEach(it => { kinds[it.kind] = (kinds[it.kind] || 0) + 1; });
    const repTypes = types.filter(t => t.rounds > 1).map(t => t.type);
    const onRep = repTypes.filter(t => items.some(it => it.type === t)).length;
    return { wrong: rows.length, areas: areas.length, n: items.length, kinds,
             byArea, maxArea: Math.max.apply(null, Object.values(byArea)),
             onAreas: Object.keys(byArea).length,
             repTypes: repTypes.length, onRep,
             topAreas: areas.slice(0, 3).map(g => g.area),
             topOn: areas.slice(0, 3).every(g => !!byArea[g.area]) };
  });
  chk('틀린 문항을 회차를 가로질러 모은다', plan.wrong >= 20, '모은 문항 ' + plan.wrong);
  chk('60문항을 골랐다', plan.n === 60, '고른 문항 ' + plan.n);
  chk('원문과 동형을 둘 다 싣는다', (plan.kinds.origin || 0) > 0 && (plan.kinds.analog || 0) > 0,
      JSON.stringify(plan.kinds));
  chk('한 영역이 판을 다 먹지 않는다 (상한 ' + Math.ceil(60 / 3) + ')',
      plan.maxArea <= Math.ceil(60 / 3), '가장 많은 영역 ' + plan.maxArea + '문항 · ' + JSON.stringify(plan.byArea));
  chk('약한 영역 셋이 다 실린다', plan.topOn === true, plan.topAreas.join(' · '));
  chk('두 회차 이상에서 거듭 틀린 유형이 다 실린다',
      plan.repTypes === 0 || plan.onRep === plan.repTypes, plan.onRep + ' / ' + plan.repTypes);

  /* ── 1교시 발행 ───────────────────────────────────────── */
  await p.selectOption('#who', '검사용');
  await p.waitForTimeout(200);
  await p.click('#issue');
  for (let i = 0; i < 240 && got.length < 1; i++) await p.waitForTimeout(500);
  chk('1교시 시험지가 나온다', got.length === 1, '받은 파일 ' + got.length);
  const n1 = await p.evaluate(() => window.__names.slice());
  chk('파일 이름에 1교시와 복원 코드가 있다',
      n1.length === 1 && /1교시_시험지/.test(n1[0]) && /_[A-Z2-9]{6}\.docx$/.test(n1[0]),
      n1.join(' · '));
  await p.waitForSelector('#bx1 .cellbox input', { timeout: 30000 });

  /* ── 되살린 시험지가 발행한 것과 같다 ─────────────────
     학생이 손에 든 종이와 한 문항이라도 어긋나면 그 채점은 거짓말이 된다. */
  const same = await p.evaluate(async () => {
    const again = await w60Restore(CURP);
    const k = x => x.map(it => it.kind + '|' + it.src.id + '|' + it.src.q +
                              '|' + (it.kind === 'analog' ? (it.dhs + ':' + it.dhi) : '')).join(',');
    return { n: again.length, eq: k(again) === k(CURI) };
  });
  chk('되살린 시험지가 발행한 것과 한 문항도 다르지 않다', same.eq === true, '되살린 문항 ' + same.n);

  /* ── 1교시 채점 ───────────────────────────────────────
     세 문항에 하나꼴로 틀리게 넣는다. 그중 넷에 하나는 무응답이다. */
  const a1 = await p.evaluate(() => CURI.map((it, i) => {
    const acc = w60Accept(it), right = acc[0] || 1;
    if (i % 3 !== 0) return right;
    return (i % 12 === 0) ? 0 : ((right % 4) + 1);
  }));
  await fillBoxes(p, '#bx1', a1);
  await p.click('#save1');
  await p.waitForSelector('#bx2 .cellbox input', { timeout: 30000 });
  const st1 = await p.evaluate(() => {
    const v = w60Verdict(CURI, CURP.a1, null);
    return { saved: (CURP.a1 || []).length, wrong: v.filter(x => x !== 'know').length,
             right: v.filter(x => x === 'know').length };
  });
  chk('1교시 채점이 저장된다', st1.saved === 60, '저장된 답 ' + st1.saved);
  chk('틀린 문항이 2교시로 넘어간다', st1.wrong > 5, '틀린 문항 ' + st1.wrong);

  /* ── 2교시 되풀이 발행 ────────────────────────────────── */
  await p.click('#mk2');
  for (let i = 0; i < 240 && got.length < 2; i++) await p.waitForTimeout(500);
  chk('2교시 되풀이가 나온다', got.length === 2, '받은 파일 ' + got.length);

  /* ── 2교시 채점: 틀린 것 가운데 절반만 맞힌다 ────────── */
  const wrongIdx = await p.evaluate(() =>
    w60Verdict(CURI, CURP.a1, null).map((v, i) => v !== 'know' ? i : -1).filter(i => i >= 0));
  const a2 = await p.evaluate(({ wrongIdx }) => wrongIdx.map((gi, k) => {
    const acc = w60Accept(CURI[gi]), right = acc[0] || 1;
    return (k % 2 === 0) ? right : ((right % 4) + 1);
  }), { wrongIdx });
  await fillBoxes(p, '#bx2', a2);
  await p.click('#save2');
  await p.waitForTimeout(400);

  const want = await p.evaluate(() => {
    const v = w60Verdict(CURI, CURP.a1, CURP.a2);
    const c = { know: 0, slip: 0, none: 0, wait: 0 };
    v.forEach(x => c[x]++);
    return c;
  });
  chk('세 갈래가 모두 나온다 (판정이 한쪽으로 쏠리지 않았다)',
      want.know > 0 && want.slip > 0 && want.none > 0 && want.wait === 0, JSON.stringify(want));

  await p.click('#mkkey2');
  for (let i = 0; i < 240 && got.length < 3; i++) await p.waitForTimeout(500);
  chk('해설이 나온다', got.length === 3, '받은 파일 ' + got.length);
  const names = await p.evaluate(() => window.__names.slice());
  chk('세 파일 이름이 걸음과 복원 코드로 갈린다',
      names.length === 3 && /1교시_시험지/.test(names[0]) && /2교시_되풀이/.test(names[1])
      && /_해설_/.test(names[2]) && new Set(names).size === 3, names.join(' · '));
  chk('화면 오류 없음', errs.length === 0, errs[0] || '');
  await b.close();
  if (got.length < 3) { console.log('\n결과: 실패 ' + (fail || 1) + '건'); process.exit(1); }

  /* ── 찍어서 잰다 ─────────────────────────────────────── */
  execFileSync('soffice', ['--headless', '--convert-to', 'pdf',
    got[0].file, got[1].file, got[2].file, '--outdir', OUT], { stdio: 'ignore', timeout: 900000 });
  const paper = pdf(path.join(OUT, 'd0.pdf'));
  const retry = pdf(path.join(OUT, 'd1.pdf'));
  const key   = pdf(path.join(OUT, 'd2.pdf'));

  /* 보기(①②③④)는 문항의 일부라 당연히 있다 — '정답 ③' 꼴만 막는다. */
  const leak1 = (paper.match(/정답\s*[①②③④]/g) || []);
  const leak2 = (retry.match(/정답\s*[①②③④]/g) || []);
  chk('1교시 시험지에 정답이 한 자도 없다', leak1.length === 0, leak1.slice(0, 3).join(' · '));
  chk('2교시 되풀이에 정답이 한 자도 없다', leak2.length === 0, leak2.slice(0, 3).join(' · '));
  chk('1교시 시험지에 풀이가 없다', !/무엇을 묻는 문제인가/.test(paper), '');
  chk('1교시 시험지에 힌트가 없다', !/힌트\s*1/.test(paper), '');
  chk('1교시 표지에 복원 코드가 찍힌다', /복원 코드/.test(paper) && /[A-Z2-9]{3}-[A-Z2-9]{3}/.test(paper), '');

  /* ── 되풀이에는 힌트가 실제로 붙어 있다 ──────────────── */
  const hintN = (retry.match(/힌트\s*1\s+\S/g) || []).length;
  chk('2교시 되풀이에 문항마다 힌트가 붙는다', hintN >= Math.ceil(wrongIdx.length * 0.7),
      '힌트 붙은 문항 ' + hintN + ' / ' + wrongIdx.length);
  chk('2교시 되풀이는 1교시 번호를 그대로 쓴다',
      new RegExp('^\\s*' + (wrongIdx[wrongIdx.length - 1] + 1) + '\\s', 'm').test(retry), '');

  /* ── 머리와 그림이 같은 쪽에 있다 ────────────────────── */
  const pages = (() => { const a = paper.split('\f'); if (a.length && !a[a.length - 1].trim()) a.pop(); return a; })();
  const imgLines = execFileSync('pdfimages', ['-list', path.join(OUT, 'd0.pdf')],
    { encoding: 'utf8', maxBuffer: 32 << 20 }).split('\n').slice(2);
  const imgPg = {};
  imgLines.forEach(l => { const t = l.trim().split(/\s+/); if (t[0] && /^\d+$/.test(t[0])) imgPg[t[0]] = (imgPg[t[0]] || 0) + 1; });
  /* 크롭이 그림 하나로 안 들어가고 조각으로 쪼개져 들어갈 수 있으므로,
     쪽에 그림이 **하나라도** 있으면 그 쪽의 머리는 짝을 찾은 것으로 본다.
     머리가 있는데 그림이 아예 없는 쪽만 갈라진 쪽이다. */
  const split = [];
  pages.forEach((pg, i) => {
    /* 답안 기입란은 「 1    2    3 …」 꼴이라 이 자를 그냥 대면 머리로 잡힌다.
       실제 머리는 번호 뒤에 **글자**(영역 이름)가 온다 — 숫자면 머리가 아니다. */
    const heads = (pg.match(/^\s*\d+\s{2,}[^\d\s]/gm) || []).length;
    if (heads > 0 && !(imgPg[String(i + 1)] > 0) && !/①/.test(pg)) split.push(i + 1);
  });
  chk('문항 머리와 그 문항 그림이 같은 쪽에 있다', split.length === 0, '갈라진 쪽 ' + split.join(','));

  /* ── 해설은 정답을 다 적고, 세 갈래 판정이 맞다 ──────── */
  const keyAns = (key.match(/정답\s*[①②③④]/g) || []).length;
  chk('해설에 문항 수만큼 정답이 있다', keyAns >= 60, '적힌 정답 ' + keyAns + ' / 60');
  chk('해설에 세 갈래 판정 표가 있다', /세 갈래 판정/.test(key), '');
  chk('해설에 푼 회차 표가 있다', /푼 회차/.test(key), '');

  /* 화면이 셈한 값이 아니라 **찍힌 종이의 낱말**을 센다.
     문항 머리는 「… 정답 ①      안다」 꼴이라 같은 줄에서 잡힌다. */
  const seen = { know: 0, slip: 0, none: 0 };
  key.split('\n').forEach(l => {
    if (!/정답\s*[①②③④]/.test(l)) return;
    if (/알지만 못 꺼낸다\s*$/.test(l)) seen.slip++;
    else if (/모른다\s*$/.test(l)) seen.none++;
    else if (/안다\s*$/.test(l)) seen.know++;
  });
  chk('찍힌 해설의 판정이 화면이 셈한 것과 같다',
      seen.know === want.know && seen.slip === want.slip && seen.none === want.none,
      '종이 ' + JSON.stringify(seen) + ' · 화면 ' + JSON.stringify(want));
  chk('판정이 60문항을 다 덮는다', seen.know + seen.slip + seen.none === 60,
      '덮은 문항 ' + (seen.know + seen.slip + seen.none));

  console.log('\n결과: ' + (fail ? '실패 ' + fail + '건' : '전부 통과'));
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
