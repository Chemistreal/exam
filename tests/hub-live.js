/* ============================================================
   통합 셸 · 실제 브라우저 회귀 테스트 (playwright 가 없으면 저절로 건너뛴다)
   ------------------------------------------------------------
   셸이 파이널 앱과 맞물리는 자리는 코드를 읽어서는 확인할 수 없다. 두 창이
   같은 오리진이라는 것에 기대고 있어서, 실제로 띄워 봐야 안다.

   특히 무서운 것 하나: 셸에서 성적표를 다시 여는 길이다. 파이널은 `#r=`
   주소를 받으면 답안을 다시 채점하고 **기록을 저장한다.** 이름이 한 글자라도
   달라지면 같은 학생이 한 명 더 생긴다 — 명단이 조용히 부풀고, 또래 인원이
   늘고, 석차가 틀어진다. 열어 보고 기록 수가 그대로인지 센다.

   여기서 지키는 것:
   - 성적표를 열어도 기록이 늘지 않는다
   - 연 화면이 곧바로 덮이지 않는다(파이널의 hashchange 와 부딪히지 않는다)
   - 자료에서 채점으로 바로 넘어간다
   - 회차 표가 실제 기록과 맞는다
   - 링크 복사가 파이널이 만든 그 주소를 준다
   - 셸이 파이널의 저장 기록을 고치지 않는다
   - 채점하는 순간 숫자가 스스로 따라온다(코드로는 확인할 수 없다)

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/hub-live.js
   ============================================================ */
'use strict';
let chromium;
try { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')); }
catch (e) { console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0); }

const PORT = Number(process.env.PORT || 8931);
let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport: { width: 1200, height: 900 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));

  /* 앱스크립트를 가로챈다. DT 는 **빈 명단**으로 답한다 — 여기서 학생을 보태면
     아래 명단 검사가 흔들린다. 목적은 하나, 셸이 DT 를 몇 번 두드리는지 세는 것. */
  const dtHits = [];
  await p.route('**/macros/s/**', route => {
    const u = new URL(route.request().url());
    const cb = u.searchParams.get('callback'), act = u.searchParams.get('action');
    if (act === 'names' || act === 'pending') dtHits.push(act);
    const body = act === 'names' ? { ok: true, classes: [] }
               : act === 'pending' ? { ok: true, pending: [] }
               : { ok: true, rows: [] };
    return route.fulfill({ status: 200, contentType: 'application/javascript',
                           body: cb + '(' + JSON.stringify(body) + ')' });
  });

  /* ── 기록을 만든다 ── 파이널 앱이 쓰는 그대로 넣는다(형식이 바뀌면 여기서 걸린다) */
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 20000 });
  const seeded = await p.evaluate(() => {
    localStorage.clear();
    const put = (id, name, school, right, ts) => {
      const e = FINAL_EXAMS.find(x => x.id === id), ans = [];
      let c = 0, t = 0;
      for (let q = 1; q <= e.nQ; q++) {
        const a = (q <= right) ? (e.key[q - 1] || 1) : (((e.key[q - 1] || 1) % 4) + 1);
        ans.push(a); t++; if (okq(e, q, a)) c++;
      }
      const arr = subs(id);
      arr.push({ name, school, grade: '2', ts, correct: c, total: t, wrong: t - c, ans });
      saveSubs(id, arr);
      return c;
    };
    const now = Date.now(), D = 86400000;
    return {
      a1: put('jmchc-1', '김지성', '휘문중', 45, now - D),
      b1: put('jmchc-1', '이도현', '대원국제중', 20, now - D + 1000),
      a2: put('jmchc-2', '김지성', '휘문중', 50, now),
    };
  });

  /* networkidle 은 쓰지 않는다 — 셸이 시트·DT 를 부르므로 영영 조용해지지 않는다. */
  await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => typeof EXAMS !== 'undefined' && EXAMS.length, null, { timeout: 20000 });
  await p.waitForTimeout(1500);

  console.log('── 회차 표가 기록과 맞는다 ──');
  await p.evaluate(() => show('rnd'));
  await p.waitForTimeout(300);
  const rnd = await p.evaluate(() => [].map.call(document.querySelectorAll('#rndTable tbody tr'),
    r => [].map.call(r.querySelectorAll('td'), td => td.textContent)));
  chk('회차 두 줄', rnd.length, 2);
  chk('최근 채점한 회차가 위에', rnd[0][0], 'JMChC 모의고사 2회');
  chk('1회는 두 명', rnd[1][1], '2');
  chk('내부 이름이 새지 않는다', /jmchc/.test(rnd.map(r => r[0]).join(' ')), false);

  console.log('\n── 성적표를 열어도 기록이 늘지 않는다 ──');
  const before = await p.evaluate(() => ({
    n1: JSON.parse(localStorage.getItem('final:roster:jmchc-1') || '[]').length,
    raw: localStorage.getItem('final:roster:jmchc-1'),
  }));
  await p.evaluate(() => { show('stu'); });
  await p.waitForTimeout(400);
  await p.evaluate(() => document.querySelector('#stuList .row').click());
  await p.waitForTimeout(400);
  const card = await p.evaluate(() => ({
    name: document.getElementById('dlgName').textContent,
    stats: [].map.call(document.querySelectorAll('#dlgBody .cards .card b'), x => x.textContent),
    acts: document.querySelectorAll('#dlgBody .mini[data-act]').length,
    spark: document.querySelectorAll('#dlgBody .spark i').length,
  }));
  chk('학생 카드가 열린다', card.name, '김지성');
  chk('응시 · 평균 · 최고 · 최근', card.stats.length, 4);
  chk('두 회차 모두 단추가 있다', card.acts, 4);
  chk('추세가 그려진다', card.spark, 2);

  await p.evaluate(() => document.querySelector('#dlgBody .mini[data-act="open"]').click());
  await p.waitForTimeout(6000);
  const opened = await p.evaluate(() => {
    const f = document.querySelector('#p-exam iframe');
    return {
      tab: document.getElementById('t-exam').getAttribute('aria-selected'),
      hash: f ? f.contentWindow.location.hash.slice(0, 12) : '',
      text: f ? (f.contentDocument.getElementById('app') || { innerText: '' }).innerText.replace(/\s+/g, ' ') : '',
    };
  });
  chk('파이널 탭으로 넘어간다', opened.tab, 'true');
  chk('성적표 주소로 간다', /^#r=jmchc-/.test(opened.hash), true);
  /* 파이널의 hashchange 가 우리가 연 화면을 덮으면 시험 목록이 뜬다 */
  chk('연 화면이 덮이지 않는다', /성적표|핵심 진단/.test(opened.text), true);
  chk('그 학생 이름이 성적표에 있다', /김지성/.test(opened.text), true);

  const after = await p.evaluate(() => ({
    n1: JSON.parse(localStorage.getItem('final:roster:jmchc-1') || '[]').length,
    raw: localStorage.getItem('final:roster:jmchc-1'),
  }));
  chk('기록 수가 그대로다', after.n1, before.n1);
  chk('저장된 내용도 그대로다', after.raw === before.raw, true);

  console.log('\n── 링크 복사가 파이널이 만든 주소를 준다 ──');
  const link = await p.evaluate(async () => {
    const w = await finalWindow();
    const ex = examOf('jmchc-1');
    const rec = JSON.parse(localStorage.getItem('final:roster:jmchc-1'))[0];
    const round = { exam: 'jmchc-1', ans: rec.ans, who: { name: rec.name } };
    return { mine: w.shareLinkFinal(ex, selOf(round.ans, ex.nQ), round.who.name, ''),
             theirs: w.shareLinkFinal(ex, selOf(rec.ans, ex.nQ), rec.name, '') };
  });
  chk('셸이 만든 주소 = 파이널이 만든 주소', link.mine, link.theirs);
  chk('성적표 주소 모양이다', /final\.html#(s=[^&]+&)?r=jmchc-1\./.test(link.mine), true);

  console.log('\n── 자료에서 채점으로 바로 ──');
  await p.evaluate(() => show('mat'));
  await p.waitForTimeout(400);
  await p.evaluate(() => document.querySelector('#matTable .mini[data-grade]').click());
  await p.waitForTimeout(3000);
  const graded = await p.evaluate(() => {
    const f = document.querySelector('#p-exam iframe');
    return {
      tab: document.getElementById('t-exam').getAttribute('aria-selected'),
      head: f ? (f.contentDocument.querySelector('h2') || { textContent: '' }).textContent : '',
      omr: f ? f.contentDocument.querySelectorAll('.omr-grid .ansin').length : 0,
    };
  });
  chk('파이널 탭으로 넘어간다', graded.tab, 'true');
  chk('그 회차 답안 화면이 열린다', graded.omr > 0, true);
  chk('회차 이름이 맞는다', /회/.test(graded.head), true);

  console.log('\n── 단축키 ──');
  await p.evaluate(() => show('dash'));
  await p.click('h1');
  await p.keyboard.press('3');
  await p.waitForTimeout(200);
  chk('3 은 회차 탭', await p.evaluate(() =>
    TABS.filter(t => document.getElementById('t-' + t).getAttribute('aria-selected') === 'true')[0]), 'rnd');
  await p.keyboard.press('/');
  await p.waitForTimeout(200);
  chk('/ 는 바로 찾기', await p.evaluate(() => document.activeElement.id), 'qq');
  /* 검색창에 숫자를 치는 일은 흔하다(학년·반). 그때 탭이 튀면 치던 것이 날아간다. */
  await p.keyboard.type('2');
  await p.waitForTimeout(300);
  chk('검색창에 숫자를 쳐도 탭이 안 바뀐다', await p.evaluate(() =>
    TABS.filter(t => document.getElementById('t-' + t).getAttribute('aria-selected') === 'true')[0]), 'dash');
  chk('친 글자가 검색창에 들어간다', await p.evaluate(() => document.getElementById('qq').value), '2');
  await p.keyboard.press('Backspace');
  await p.keyboard.type('김');
  await p.waitForTimeout(300);
  chk('바로 찾기에 뜬다', await p.evaluate(() =>
    (document.querySelector('#qqList .row .nm') || { textContent: '' }).textContent), '김지성');

  console.log('\n── 채점하는 순간 스스로 따라온다 ──');
  {
    /* 여기가 이 파일의 존재 이유다. iframe 안에서 저장한 것이 부모에게
       storage 이벤트로 오는지는 띄워 봐야만 안다. 안 오면 셸의 숫자는
       새로고침 전까지 거짓말을 한다 — 채점하는 날 내내. */
    await p.evaluate(() => show('dash'));
    await p.waitForTimeout(500);
    const before = await p.evaluate(() =>
      document.querySelector('#dashCards .card b').textContent);

    await p.evaluate(() => show('exam'));
    await p.waitForTimeout(4500);
    await p.evaluate(() => {
      const f = document.querySelector('#p-exam iframe'), w = f.contentWindow, d = f.contentDocument;
      w.openExam('jmchc-5');
      d.getElementById('nm').value = '새학생'; d.getElementById('sch').value = 'Z중';
      for (let q = 1; q <= 60; q++) w.setAns(q, 1);
      w.scoreAuto();
    });
    await p.waitForTimeout(1500);
    /* 대시보드 탭으로 가지도 않았는데 이미 바뀌어 있어야 한다 */
    const after = await p.evaluate(() =>
      document.querySelector('#dashCards .card b').textContent);
    chk('대시보드로 가지 않아도 숫자가 바뀐다', Number(after) > Number(before), true);

    await p.evaluate(() => show('rnd'));
    await p.waitForTimeout(400);
    chk('회차 표에도 새 회차가 늘었다', await p.evaluate(() =>
      [].some.call(document.querySelectorAll('#rndTable tbody tr td:first-child'),
        td => /5회/.test(td.textContent))), true);
  }

  console.log('\n── 갈라진 이름을 셸이 짚어 준다 ──');
  {
    await p.evaluate(() => {
      // 같은 학생을 '김 지성' 으로 한 번 더 저장한다(파이널 앱이 쓰는 형식 그대로)
      const arr = JSON.parse(localStorage.getItem('final:roster:jmchc-2'));
      const r = arr[0];
      arr.push(Object.assign({}, r, { name: '김 지성', ts: r.ts + 1000 }));
      localStorage.setItem('final:roster:jmchc-2', JSON.stringify(arr));
      refreshLocal();
    });
    await p.waitForTimeout(400);
    chk('합쳐야 할 이름에 뜬다', await p.evaluate(() =>
      !document.getElementById('mergeWrap').hidden), true);
    chk('두 이름표를 다 적는다', await p.evaluate(() => {
      const t = (document.querySelector('#mergeList .row') || { textContent: '' }).textContent;
      return /김지성/.test(t) && /김 지성/.test(t);
    }), true);
  }

  console.log('\n── 시트 상태를 늘 보여 준다 ──');
  {
    const bar = await p.evaluate(() =>
      document.getElementById('syncMsg').textContent.replace(/\s+/g, ' ').trim());
    chk('맞춘 적 없으면 그렇게 말한다', /아직 시트와 맞춘 적이 없습니다|시트에서 불러오는 중|마지막으로 맞춘/.test(bar), true);
    chk('지금 맞추기 단추가 있다', await p.evaluate(() => !!document.getElementById('syncNow')), true);
  }

  console.log('\n── DT 를 다시 그릴 때마다 두드리지 않는다 ──');
  {
    /* 재어 보니 셸을 여는 것만으로 13번이 나갔다. 앱스크립트는 실행을 한 줄로
       세우니 뒤엣것은 한참을 기다리고, 그동안 DT 숫자는 '…' 로 돌아가 있다. */
    console.log('  연 뒤까지 DT 호출 ' + dtHits.length + '회 · ' + JSON.stringify(dtHits));
    chk('여는 데 명단·미완료 한 번씩이면 된다', dtHits.length <= 2, true);
    dtHits.length = 0;
    for (const t of ['stu', 'rnd', 'dash', 'stu', 'dash']) {
      await p.evaluate(id => show(id), t);
      await p.waitForTimeout(350);
    }
    chk('탭을 오가도 다시 묻지 않는다', dtHits, []);
    // 이미 아는 숫자를 물음표로 되돌리면 채점하는 날 내내 '…' 만 보인다
    const shown = await p.evaluate(() => (document.getElementById('dtCnt') || {}).textContent);
    chk('DT 숫자가 …로 돌아가지 않는다', shown, '0');
  }

  console.log('\n── 이 숫자가 어디까지의 숫자인지 적는다 ──');
  {
    const src = await p.evaluate(() => (document.getElementById('srcNote') || {}).textContent || '');
    console.log('  ' + src);
    chk('숫자 밑에 출처가 적힌다',
        /이 브라우저 기록만|시트까지 반영된|받아오는 중/.test(src), true);
  }

  chk('콘솔에 예외가 없다', errs.filter(e => !/Failed to fetch|ERR_/.test(e)), []);
  await b.close();
  console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
  process.exit(fail ? 1 : 0);
})();
