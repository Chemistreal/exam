/* ============================================================
   명단 관리 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   이름을 잘못 입력하면 고칠 방법이 없었다. 그런데 이름이 틀리면 그 학생의
   기록이 **둘로 갈라진다** — 성장 추적·숙달 추적·되풀이되는 오개념은 전부
   이름이 같은지로 같은 학생을 잇기 때문이다. 한 글자 오타 하나에 지난
   회차가 통째로 안 보인다.

   가장 조심할 곳은 시트다. 이름을 고쳐도 구글 시트에는 옛 이름 행이 그대로
   남아 있고, '시트에서 불러오기'는 중복을 **이름+답안**으로 판정한다.
   (동기화 키는 없앴다 — 시트는 URL 을 아는 누구에게나 열려 있다.)
   그대로 두면 고쳐 놓은 것이 되살아나는 게 아니라 오타 이름이 하나 더
   생긴다. 그래서 고친 내역을 남겨 두고 받아올 때 바꿔 넣는다.

   여기서 지키는 것:
   - 띄어쓰기 차이는 저절로 합쳐진다(nameKey) — 찾아 줄 것이 아니다
   - 한 글자 다른 이름은 찾아 준다(동명이인일 수 있어 기계가 합치지 않는다)
   - 합치면 전 회차가 한 사람으로 묶인다
   - 합친 뒤 시트에서 다시 받아도 옛 이름이 되살아나지 않는다
   - 회차별 기록을 고치고 지울 수 있다
   - 학생을 통째로 지울 수 있다(이름을 다시 받아 확인한다)
   - 이름·학교·학년이 모두 같아야 같은 학생이다
   - 채점을 두 번 해서 쌓인 겹친 기록을 한 줄로 줄인다
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
catch (e) {
  /* 브라우저를 깔아 놓고도 조용히 건너뛰면 초록불이 '브라우저 검사까지
     통과했다' 로 읽힌다. 실제로 그랬다 — 통합 셸의 브라우저 검사가 몇 달
     동안 CI 에서 한 번도 안 돌았는데 초록불이었다. 깔아 둔 자리에서는 멈춘다. */
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

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
  [['jmchc-6', [['김지성', 'X중', 1], ['김지 성', 'X중', 2], ['이도현', 'X중', 3], ['이도헌', 'X중', 4]]],
   ['jmchc-7', [['김지성', 'X중', 5], ['이도현', 'X중', 6]]]].forEach(([id, people]) => {
    const ex = FINAL_EXAMS.find(e => e.id === id), miss = new Set(ex.miss || []), arr = [];
    people.forEach(([nm, sch, s]) => {
      const a = mk(ex, s); let c = 0, t = 0;
      for (let q = 1; q <= ex.nQ; q++) { if (miss.has(q)) continue; t++; if (okq(ex, q, a[q - 1])) c++; }
      arr.push({ name: nm, school: sch, grade: '3', ts: 1700000000000 + s * 86400000,
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
  /* '김지 성' 은 이제 저장·비교 모두 공백을 지우므로 '김지성' 과 한 사람이다.
     갈리는 것은 한 글자가 다른 '이도헌' 뿐이라 셋이 된다. */
  chk('학생 수', num(t, /학생 (\d+)명/), 3);
  chk('띄어쓰기는 저절로 합쳐졌다', /김지 성/.test(t), false);
  chk('기록 건수', num(t, /기록 (\d+)건/), 6);
  chk('비슷한 이름을 찾아낸다', num(t, /비슷한 이름 (\d+)쌍/), 1);
  chk('띄어쓰기는 짚지 않는다(이미 합쳐졌다)', /띄어쓰기만 다름/.test(t), false);
  chk('한 글자 차이를 짚는다', /한 글자 다름/.test(t), true);

  console.log('\n── 합치기 ──');
  /* 한 글자 차이는 사람이 판단해 합친다 — 동명이인일 수 있어서 기계가
     합치면 되돌릴 수 없다. */
  await page.evaluate(() => rosterMergeAt(window.__rnames.findIndex(k => rosterLabel(k).name === '이도헌'), window.__rnames.findIndex(k => rosterLabel(k).name === '이도현')));
  await page.waitForTimeout(400);
  t = await txt();
  chk('학생이 하나로 줄었다', num(t, /학생 (\d+)명/), 2);
  chk('기록은 하나도 안 없어졌다', num(t, /기록 (\d+)건/), 6);
  const merged = await page.evaluate(() => subs('jmchc-6').map(r => r.name));
  chk('jmchc-6 이름들', merged, ['김지성', '김지 성', '이도현', '이도현']);
  chk('고침 기록이 남는다', await page.evaluate(() => JSON.parse(localStorage.getItem('final:renames') || '{}')),
      { '이도헌': '이도현' });

  /* 여기가 핵심이다. 시트에는 '김지 성' 행이 그대로 있다. 다시 받아오면
     중복 판정이 이름+답안이라 '다른 사람'으로 보고 새로 넣어 버린다. */
  console.log('\n── 시트에서 다시 받아오기 ──');
  const resync = await page.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-6');
    const row = subs('jmchc-6').find(r => r.name === '이도현');
    const added = mergeSheetRows(ex, [{ name: '이도헌', answers: row.ans.join(''), ts: 1 }]);
    /* 띄어쓰기가 든 행도 시트에 그대로 남아 있다. 받아올 때 다듬으므로
       '김지 성' 이 새 사람으로 들어오지 않는다. */
    const row2 = subs('jmchc-6').find(r => r.name === '김지성');
    const added2 = mergeSheetRows(ex, [{ name: '김 지 성', answers: row2.ans.join(''), ts: 1 }]);
    return { added, added2, names: subs('jmchc-6').map(r => r.name) };
  });
  chk('옛 이름 행이 새로 들어오지 않는다', resync.added, 0);
  chk('오타가 되살아나지 않는다', resync.names.indexOf('이도헌'), -1);
  chk('띄어쓰기 행도 새로 안 들어온다', resync.added2, 0);
  chk('띄어쓴 이름이 생기지 않는다', resync.names.indexOf('김 지 성'), -1);

  console.log('\n── 이름 일괄 고치기 ──');
  const renamed = await page.evaluate(() => {
    const key = window.__rnames.find(k => rosterLabel(k).name === '이도현');
    const n = rosterApply(key, r => { r.name = '이도현2'; });
    return { n, six: subs('jmchc-6').map(r => r.name), seven: subs('jmchc-7').map(r => r.name) };
  });
  // 앞에서 이도헌을 합쳤으므로 이도현 기록이 셋이다
  chk('전 회차가 함께 바뀐다', renamed.n, 3);
  chk('jmchc-6 반영', renamed.six.indexOf('이도현2') >= 0, true);
  chk('jmchc-7 반영', renamed.seven.indexOf('이도현2') >= 0, true);

  console.log('\n── 기록 수정·삭제 ──');
  const del = await page.evaluate(() => {
    const before = subs('jmchc-7').length;
    const arr = subs('jmchc-7'); arr.splice(0, 1); saveSubs('jmchc-7', arr);
    return { before, after: subs('jmchc-7').length };
  });
  chk('한 건만 지워진다', [del.before, del.after], [2, 1]);

  console.log('\n── 학생 통째로 지우기 ──');
  {
    // 이 앱에서 가장 되돌리기 어려운 동작이라 이름을 다시 받아 확인한다.
    // 확인창을 눌러 넘기는 것만으로는 지워지면 안 된다.
    await page.evaluate(SEED);
    await page.evaluate(() => { location.hash = ''; location.hash = '#roster'; });
    await page.waitForTimeout(500);
    const before = await page.evaluate(() => [subs('jmchc-6').length, subs('jmchc-7').length]);

    // 1) 이름을 틀리게 적으면 아무것도 안 지운다
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.accept('엉뚱한이름'));
    await page.evaluate(() => rosterDelName(window.__rnames.find(k => rosterLabel(k).name === '김지성')));
    await page.waitForTimeout(400);
    chk('이름이 다르면 안 지운다', await page.evaluate(() => [subs('jmchc-6').length, subs('jmchc-7').length]), before);

    // 2) 취소하면 안 지운다
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.dismiss());
    await page.evaluate(() => rosterDelName(window.__rnames.find(k => rosterLabel(k).name === '김지성')));
    await page.waitForTimeout(400);
    chk('취소하면 안 지운다', await page.evaluate(() => [subs('jmchc-6').length, subs('jmchc-7').length]), before);

    // 3) 이름을 그대로 적으면 전 회차가 없어진다
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.accept('김지성'));
    await page.evaluate(() => rosterDelName(window.__rnames.find(k => rosterLabel(k).name === '김지성')));
    await page.waitForTimeout(600);
    const after = await page.evaluate(() => ({
      six: subs('jmchc-6').map(r => r.name), seven: subs('jmchc-7').map(r => r.name),
      text: document.body.innerText }));
    chk('jmchc-6 에서 없어졌다', after.six.indexOf('김지성'), -1);
    chk('jmchc-7 에서도 없어졌다', after.seven.indexOf('김지성'), -1);
    /* '김지 성' 도 '김지성' 과 한 사람이므로 함께 없어진다 */
    chk('띄어쓴 표기도 함께 없어졌다', after.six.indexOf('김지 성'), -1);
    chk('남의 기록은 그대로', after.six, ['이도현', '이도헌']);
    chk('학생 수가 줄었다', Number((after.text.match(/학생 (\d+)명/) || [])[1]), 2);
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.accept(d.type() === 'prompt' ? '고친이름' : undefined));
  }

  /* ── 정체성: 이름 + 학교 + 학년 ────────────────────────────────────
     선생님이 정한 규칙이다. 같은 이름이라도 학교·학년이 다르면 다른 사람이고,
     이름만 있고 학교·학년이 비어 있으면 또 다른 사람이다. 실제 명단이
     이렇게 갈려 있었다 — 같은 학생인데 '과천중 2학년' 줄과 '-' 줄로. */
  console.log('\n── 이름·학교·학년이 모두 같아야 같은 학생 ──');
  {
    await page.evaluate(() => {
      localStorage.clear();
      const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-1');
      const mk = s => { let x = (s * 2654435761) >>> 0, a = [];
        for (let i = 0; i < ex.nQ; i++) { x = (x * 1664525 + 1013904223) >>> 0; a.push((x >>> 16) % 4 + 1); }
        return a; };
      const row = (nm, sch, grd, s) => { const a = mk(s), miss = new Set(ex.miss || []);
        let c = 0, t = 0;
        for (let q = 1; q <= ex.nQ; q++) { if (miss.has(q)) continue; t++; if (okq(ex, q, a[q - 1])) c++; }
        return { name: nm, school: sch, grade: grd, ts: 1000 + s, correct: c, total: t, wrong: t - c, ans: a }; };
      saveSubs('jmchc-1', [
        row('이서준', '과천중', '2', 1),   // A
        row('이서준', '', '', 1),          // 학교·학년이 비었다 → 따로 센다 (같은 답안이라 겹침이기도 하다)
        row('이서준', '분당중', '3', 7),   // 동명이인 → 따로
      ]);
    });
    await page.evaluate(() => { location.hash = ''; location.hash = '#roster'; });
    await page.waitForTimeout(600);
    const t2 = await txt();
    chk('셋으로 나뉜다', num(t2, /학생 (\d+)명/), 3);
    chk('학교·학년 없음을 표시한다', /학교·학년 없음/.test(t2), true);
    chk('동명이인이 안 합쳐진다', /분당중/.test(t2) && /과천중/.test(t2), true);
    chk('학교·학년만 비어 있다고 짚어 준다', /학교·학년만 비어 있음/.test(t2), true);

    /* 빈 줄은 과천중·분당중 어느 쪽일지 모르므로 둘 다 짝으로 짚는다(고르는 건
       선생님 몫이다). 다만 **학교가 서로 다른 동명이인끼리는 절대 짝이 아니다** —
       그 둘을 합치라고 권하면 다른 사람의 기록이 섞인다. */
    const pairs = await page.evaluate(() => nameSuspects(window.__rnames)
      .map(s => [rosterLabel(window.__rnames[s.ia]).where, rosterLabel(window.__rnames[s.ib]).where, s.why]));
    chk('빈 줄은 양쪽 다 후보로 짚는다', pairs.length, 2);
    chk('모두 같은 이유', Array.from(new Set(pairs.map(p => p[2]))), ['학교·학년만 비어 있음']);
    chk('학교가 다른 동명이인은 짝이 아니다',
        pairs.some(p => p[0] && p[1] && p[0] !== p[1]), false);
  }

  console.log('\n── 겹친 기록 정리 ──');
  {
    const before = await page.evaluate(() => ({ dup: rosterDupes().length, n: subs('jmchc-1').length }));
    chk('겹친 묶음을 찾아낸다', before.dup, 1);
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.accept());
    await page.evaluate(() => rosterDedupe());
    await page.waitForTimeout(700);
    const after = await page.evaluate(() => ({
      dup: rosterDupes().length,
      rows: subs('jmchc-1').map(r => r.name + '|' + r.school + '|' + r.grade) }));
    chk('겹침이 사라진다', after.dup, 0);
    // 학교·학년이 적힌 줄을 남긴다 — 그 줄만이 누구인지 말해 준다
    chk('채워진 줄을 남긴다', after.rows, ['이서준|과천중|2', '이서준|분당중|3']);
    page.removeAllListeners('dialog');
    page.on('dialog', d => d.accept(d.type() === 'prompt' ? '고친이름' : undefined));
  }

  console.log('\n── 백업 ──');
  // 앞 절이 localStorage 를 비우고 한 시험만 심었다. 백업은 여러 시험을 담는지
  // 보는 것이므로 다시 심고 시작한다.
  await page.evaluate(SEED);
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
    // 앞 단계들이 기록을 지우고 고쳤으므로 개수를 고정해 두면 안 된다.
    // 백업 직전 상태로 돌아왔는지를 본다.
    return { ids: Object.keys(out.rosters).length, empty,
             was: (out.rosters['jmchc-6'] || []).length, back: subs('jmchc-6').length };
  });
  chk('백업에 시험이 담긴다', backup.ids >= 2, true);
  chk('지우면 비워진다', backup.empty, 0);
  chk('되돌리면 그대로 돌아온다', backup.back, backup.was);
  chk('되돌린 뒤 비어 있지 않다', backup.back > 0, true);

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
  await page.evaluate(() => rosterApply(window.__rnames.find(k => rosterLabel(k).name === '김지성'), r => { r.name = '김지성A'; }));
  await page.evaluate(() => sheetCall({ action: 'rename', from: '김지성', to: '김지성A' }, function () {}));
  await page.waitForTimeout(300);
  const sent = await page.evaluate(() => window.__sent.map(u => u.replace(/^[^?]*\?/, '')));
  chk('시트로 요청이 나간다', sent.length >= 1, true);
  chk('이름 고치기 동작', /action=rename/.test(sent[0] || ''), true);
  chk('옛 이름을 보낸다', /from=%EA%B9%80%EC%A7%80%EC%84%B1(&|$)/.test(sent[0] || ''), true);
  // 동기화 키는 없앴다. 남아 있으면 시트가 안 받는 값을 쓸데없이 보내는 것이다.
  chk('키는 이제 안 보낸다', /(^|&)key=/.test(sent[0] || ''), false);
  chk('콜백 이름을 붙인다', /(^|&)callback=__fsheet/.test(sent[0] || ''), true);

  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
