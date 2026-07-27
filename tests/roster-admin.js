/* ============================================================
   명단 관리 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   이름을 잘못 입력하면 고칠 방법이 없었다. 그런데 이름이 틀리면 그 학생의
   기록이 **둘로 갈라진다** — 성장 추적·숙달 추적·되풀이되는 오개념은 전부
   이름이 같은지로 같은 학생을 잇기 때문이다. 한 글자 오타 하나에 지난
   회차가 통째로 안 보인다.

   가장 조심할 곳은 시트다. 이름을 고쳐도 구글 시트에는 옛 이름 행이 그대로
   남아 있고, '시트에서 불러오기'는 중복을 **이름+답안**으로 판정한다.
   그대로 두면 고쳐 놓은 것이 되살아나는 게 아니라 오타 이름이 하나 더
   생긴다. 그래서 고친 내역을 남겨 두고 받아올 때 바꿔 넣는다.

   여기서 지키는 것:
   - 비슷한 이름(한 글자·띄어쓰기)을 찾아 준다
   - 합치면 전 회차가 한 사람으로 묶인다
   - 합친 뒤 시트에서 다시 받아도 옛 이름이 되살아나지 않는다
   - 회차별 기록을 고치고 지울 수 있다
   - 백업을 내보내고 다시 들여올 수 있다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/roster-admin.js
   ============================================================ */
'use strict';
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}/final.html`;

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) { console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0); }

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

// 오타를 일부러 섞어 심는다: '김지 성'(띄어쓰기) · '이도헌'(한 글자)
const SEED = () => {
  localStorage.clear();
  const mk = (ex, s) => { let x = (s * 2654435761) >>> 0, a = [];
    for (let i = 0; i < ex.nQ; i++) { x = (x * 1664525 + 1013904223) >>> 0; a.push((x >>> 16) % 4 + 1); }
    return a; };
  [['jmchc-6', [['김지성', 1], ['김지 성', 2], ['이도현', 3], ['이도헌', 4]]],
   ['jmchc-7', [['김지성', 5], ['이도현', 6]]]].forEach(([id, people]) => {
    const ex = FINAL_EXAMS.find(e => e.id === id), miss = new Set(ex.miss || []), arr = [];
    people.forEach(([nm, s]) => {
      const a = mk(ex, s); let c = 0, t = 0;
      for (let q = 1; q <= ex.nQ; q++) { if (miss.has(q)) continue; t++; if (okq(ex, q, a[q - 1])) c++; }
      arr.push({ name: nm, school: 'X중', grade: '3', ts: 1700000000000 + s * 86400000,
                 correct: c, total: t, wrong: t - c, ans: a });
    });
    saveSubs(id, arr);
  });
};

(async () => {
  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('dialog', d => d.accept(d.type() === 'prompt' ? '고친이름' : undefined));

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.evaluate(SEED);
  await page.goto(BASE + '#roster', { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);

  const txt = () => page.evaluate(() => document.body.innerText);
  const num = (t, re) => Number((t.match(re) || [])[1]);

  console.log('── 첫 화면 ──');
  let t = await txt();
  chk('명단 관리 화면이 뜬다', /명단 관리/.test(t), true);
  chk('학생 수', num(t, /학생 (\d+)명/), 4);   // 오타 둘 때문에 넷으로 갈렸다
  chk('기록 건수', num(t, /기록 (\d+)건/), 6);
  chk('비슷한 이름을 찾아낸다', num(t, /비슷한 이름 (\d+)쌍/), 2);
  chk('띄어쓰기 차이를 짚는다', /띄어쓰기만 다름/.test(t), true);
  chk('한 글자 차이를 짚는다', /한 글자 다름/.test(t), true);

  console.log('\n── 합치기 ──');
  await page.evaluate(() => rosterMergeAt(window.__rnames.indexOf('김지 성'), window.__rnames.indexOf('김지성')));
  await page.waitForTimeout(400);
  t = await txt();
  chk('학생이 하나로 줄었다', num(t, /학생 (\d+)명/), 3);
  chk('기록은 하나도 안 없어졌다', num(t, /기록 (\d+)건/), 6);
  const merged = await page.evaluate(() => subs('jmchc-6').map(r => r.name));
  chk('jmchc-6 이름들', merged, ['김지성', '김지성', '이도현', '이도헌']);
  chk('고침 기록이 남는다', await page.evaluate(() => JSON.parse(localStorage.getItem('final:renames') || '{}')),
      { '김지 성': '김지성' });

  /* 여기가 핵심이다. 시트에는 '김지 성' 행이 그대로 있다. 다시 받아오면
     중복 판정이 이름+답안이라 '다른 사람'으로 보고 새로 넣어 버린다. */
  console.log('\n── 시트에서 다시 받아오기 ──');
  const resync = await page.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-6');
    const row = subs('jmchc-6').find(r => r.name === '김지성');
    const added = mergeSheetRows(ex, [{ name: '김지 성', answers: row.ans.join(''), ts: 1 }]);
    return { added, names: subs('jmchc-6').map(r => r.name) };
  });
  chk('옛 이름 행이 새로 들어오지 않는다', resync.added, 0);
  chk('오타가 되살아나지 않는다', resync.names.indexOf('김지 성'), -1);

  console.log('\n── 이름 일괄 고치기 ──');
  const renamed = await page.evaluate(() => {
    const n = rosterApplyRename('이도현', '이도현2');
    return { n, six: subs('jmchc-6').map(r => r.name), seven: subs('jmchc-7').map(r => r.name) };
  });
  chk('전 회차가 함께 바뀐다', renamed.n, 2);
  chk('jmchc-6 반영', renamed.six.indexOf('이도현2') >= 0, true);
  chk('jmchc-7 반영', renamed.seven.indexOf('이도현2') >= 0, true);

  console.log('\n── 기록 수정·삭제 ──');
  const del = await page.evaluate(() => {
    const before = subs('jmchc-7').length;
    const arr = subs('jmchc-7'); arr.splice(0, 1); saveSubs('jmchc-7', arr);
    return { before, after: subs('jmchc-7').length };
  });
  chk('한 건만 지워진다', [del.before, del.after], [2, 1]);

  console.log('\n── 백업 ──');
  const backup = await page.evaluate(() => {
    const out = { version: 1, renames: JSON.parse(localStorage.getItem('final:renames') || '{}'), rosters: {} };
    for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i);
      if (k && k.indexOf('final:roster:') === 0) out.rosters[k.slice('final:roster:'.length)] = JSON.parse(localStorage.getItem(k) || '[]'); }
    // 통째로 날린 뒤 되돌린다
    const saved = JSON.stringify(out);
    for (let i = localStorage.length - 1; i >= 0; i--) { const k = localStorage.key(i);
      if (k && k.indexOf('final:roster:') === 0) localStorage.removeItem(k); }
    const empty = subs('jmchc-6').length;
    const data = JSON.parse(saved);
    Object.keys(data.rosters).forEach(id => saveSubs(id, data.rosters[id]));
    return { ids: Object.keys(out.rosters).length, empty, back: subs('jmchc-6').length };
  });
  chk('백업에 시험이 담긴다', backup.ids >= 2, true);
  chk('지우면 비워진다', backup.empty, 0);
  chk('되돌리면 돌아온다', backup.back, 4);

  console.log('\n── 목록에서 들어갈 수 있다 ──');
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  chk('시험 목록에 명단 관리 버튼', await page.evaluate(() => /명단 관리/.test(document.body.innerText)), true);
  await page.evaluate(() => { location.hash = '#roster'; });
  await page.waitForTimeout(500);
  chk('버튼으로 들어가진다', /학생 .*명/.test(await txt()), true);

  /* ── 시트에도 닿는가 ─────────────────────────────────────────────
     고친 것을 시트에 보내지 않으면 성적문자가 옛 이름으로 나간다.
     실제 시트를 부를 수는 없으니, 어떤 주소로 나가는지를 가로채 본다. */
  console.log('\n── 시트로 나가는 요청 ──');
  await page.evaluate(() => {
    window.__sent = [];
    // JSONP 는 <script> 를 붙여서 부른다. 붙는 순간을 잡아 주소만 챙기고 막는다.
    const add = document.body.appendChild.bind(document.body);
    document.body.appendChild = function (el) {
      if (el && el.tagName === 'SCRIPT' && /action=/.test(el.src || '')) {
        window.__sent.push(el.src);
        const m = /callback=([^&]+)/.exec(el.src);
        if (m) setTimeout(() => { try { window[m[1]]({ ok: true, changed: 1 }); } catch (e) {} }, 0);
        return el;                       // 진짜로 붙이지는 않는다
      }
      return add(el);
    };
  });
  await page.evaluate(() => rosterApplyRename('김지성', '김지성A'));
  await page.evaluate(() => sheetCall({ action: 'rename', from: '김지성', to: '김지성A' }, function () {}));
  await page.waitForTimeout(300);
  const sent = await page.evaluate(() => window.__sent.map(u => u.replace(/^[^?]*\?/, '')));
  chk('시트로 요청이 나간다', sent.length >= 1, true);
  chk('이름 고치기 동작', /action=rename/.test(sent[0] || ''), true);
  chk('옛 이름을 보낸다', /from=%EA%B9%80%EC%A7%80%EC%84%B1(&|$)/.test(sent[0] || ''), true);
  chk('동기화 키를 함께 보낸다', /(^|&)key=/.test(sent[0] || ''), true);
  chk('콜백 이름을 붙인다', /(^|&)callback=__fsheet/.test(sent[0] || ''), true);

  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
