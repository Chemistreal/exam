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
  /* 서비스 워커를 막는다. 여기서는 오프라인 캐시를 보지 않는데(그건 offline.js),
     로컬 서버는 저장소 루트를 그대로 서빙해서 워커 범위가 '/' 가 된다. 그러면
     워커가 ../DT/ 요청까지 가로채 검사용 흉내 화면이 안 뜬다.
     실제 배포에서는 워커 범위가 /exam/ 이라 ../DT/ 는 애초에 안 걸린다. */
  const ctx = await b.newContext({ viewport: { width: 1200, height: 900 },
                                   permissions: ['clipboard-read', 'clipboard-write'],
                                   serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));

  /* 앱스크립트를 가로챈다. DT 는 **빈 명단**으로 답한다 — 여기서 학생을 보태면
     아래 명단 검사가 흔들린다. 목적은 하나, 셸이 DT 를 몇 번 두드리는지 세는 것. */
  const dtHits = [];
  const DT_EP = 'AKfycbzvFaPXgEgCBQ8HowtP8tPTtdiIVFtmZSUf0KFXUOVOh3ektrFMkz4KSR4I52LDBzB8rw';
  /* 셸은 이제 DT 의 자료 목록을 읽어 자료 탭을 그린다(다른 저장소라 여기엔 없다).
     실제 규칙 그대로 흉내 낸다 — 화학Ⅱ 12회는 **해설 HTML 이 없고 PDF 만** 있다. */
  await p.route('**/DT/materials.json', route => route.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({ kinds: [], extra: [], courses: [
      { key:'ch1', name:'화학Ⅰ', rounds:[
        { round:1, files:{ munje:{html:'munje_ch1_round01.html'}, haeseol:{html:'haeseol_ch1_round01.html'},
                           omr:{html:'omr_ch1_round01.html'} } }] },
      { key:'ch2', name:'화학Ⅱ', rounds:[
        { round:1,  files:{ munje:{html:'munje_ch2_round01.html'}, haeseol:{html:'haeseol_ch2_round01.html'} } },
        { round:12, files:{ munje:{html:'munje_ch2_round12.html'}, haeseol:{pdf:'haeseol_ch2_round12.pdf'} } }] },
      { key:'gc', name:'일반화학', rounds:[] },
    ] }),
  }));
  /* 문구는 DT 의 pending.html 이 갖고 있고 셸은 **빌려 쓴다.** 이 저장소에는 DT 가
     없으므로(다른 저장소다) 그 화면을 흉내 내 세워 둔다. 볼 것은 문구의 내용이
     아니라 **빌리는 길이 실제로 이어지는가** 다 — 문구 자체는 DT 저장소가 본다.
     ⚠ 반드시 **첫 화면을 열기 전에** 걸어 둔다. 셸은 이 화면을 탭으로도 얹으므로
     탭을 한 번 지나가면 그때 붙은 iframe 이 그대로 남는다. 뒤늦게 걸면 이미 404 를
     문 창을 빌리게 되어 문자가 통째로 안 만들어진다(실제로 그렇게 깨졌다). */
  await p.route('**/DT/pending.html', route => route.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8"><script>'
        + 'function shareMsg(d,stage){ return "빌린재시:"+d.name+"/"+d.course+"/"+d.round+"/"+d.next+"/"+stage; }'
        + 'function passMsg(d){ return "빌린통과:"+d.name+"/"+d.course+"/"+d.round+"/"+d.att+"/"+d.tries+"/"+d.score; }'
        + 'function examLink(c,r){ return "빌린주소/"+c+"/"+r; }'
        + 'function absentMsg(d,stage){ return "빌린미응시:"+(d.name||"반전체")+"/"+d.course+"/"+d.round+"/"+d.link+"/"+stage; }'
        + '</script>',
    }));
  await p.route('**/DT/roster.html', route => route.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8"><title>반 명단</title><h1>반 명단</h1>',
  }));
  await p.route('**/macros/s/**', route => {
    const u = new URL(route.request().url());
    const cb = u.searchParams.get('callback'), act = u.searchParams.get('action');
    const isDT = u.pathname.includes(DT_EP);
    // KMChC 도 'names' 를 쓴다. 앱을 가려 세지 않으면 이 검사가 뭘 세는지 모른다.
    if (isDT && (act === 'names' || act === 'pending')) dtHits.push(act);
    const D = 86400000, now = Date.now();
    const body = (isDT && act === 'names') ? { ok: true, classes: [] }
               /* KMChC: 이 시트에는 학교 열이 **없다.** 같은 이름의 파이널 학생과
                  한 줄로 붙어야 한다 — 안 붙으면 셸에 같은 아이가 두 줄로 뜨고,
                  어느 줄을 눌러도 기록이 반쪽이다. */
               : act === 'names' ? { ok: true, students: [
                   { id: 'k1', name: '김지성', grade: '중2', kind: '실제',
                     link: 'https://chemistreal.github.io/KMChC/report.html?id=k1', ts: 0 } ] }
               /* DT 가 실제로 주는 모양이다 — {active, stale, …} 객체. 배열로
                  흉내 내면 'DT 미완료' 가 undefined 로 찍히던 버그를 못 잡는다. */
               : act === 'pending' ? { ok: true, pending: { activeDays: 14, generatedAt: 'T', stale: [], active: [
                   { studentKey: 's1', name: '최예린', school: '역삼중', year: '2', course: 'ch1', round: 12,
                     lastAttempt: '정시', nextNeeded: '재시', score: 68, days: 3, lastDate: '6/17',
                     reportLink: 'https://x/report.html?student=a', active: true } ] } }
               /* 통과·미응시를 **파이널에도 있는 학생**(김지성)으로 둔다. 학생 카드가
                  세 앱을 한 장에 모으는지 보려면 같은 아이여야 한다. 학교는 일부러
                  짧게 준다 — DT 는 실제로 '휘문' 과 '휘문중' 을 섞어서 준다. */
               : act === 'passed' ? { ok: true, passed: { days: 14, generatedAt: 'T', passed: [
                   { name: '김지성', school: '휘문', year: '2', course: 'ch2', round: 7, attempt: '정시',
                     tries: 1, score: 96, date: '6/19', days: 1, reportLink: 'https://x/report.html?student=b' } ] } }
               : act === 'absentees' ? { ok: true, absentees: { generatedAt: 'T', classes: [
                   { label: '화학1 토1:30-5:30', course: 'ch1', round: 12, total: 8, present: 6, absent: ['김도윤', '김지성'] },
                   { label: '화학2 일6-10', course: 'ch2', round: 7, total: 6, present: 6, absent: [] } ] } }
               : act === 'cohortmis' ? { ok: true, rows: [
                   { studentKey: 's1', date: new Date(now - 2 * D).toISOString(), wrongMis: ['몰농도', '완충'] },
                   { studentKey: 's2', date: new Date(now - 3 * D).toISOString(), wrongMis: ['몰농도'] },
                 ] }
               : { ok: true, rows: [] };
    return route.fulfill({ status: 200, contentType: 'application/javascript',
                           body: cb + '(' + JSON.stringify(body) + ')' });
  });

  /* ── 기록을 만든다 ── 파이널 앱이 쓰는 그대로 넣는다(형식이 바뀌면 여기서 걸린다) */
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 20000 });
  const seeded = await p.evaluate(() => {
    localStorage.clear();
    /* 셸도 파이널과 **같은 열쇠칸**을 쓴다. 여기서 한 번 넣어 두면 셸이 다시
       묻지 않는다 — 갈라져 있으면 이 줄이 안 먹고 셸이 잠긴 채로 남는다. */
    localStorage.setItem('chemistreal:gate', String(Date.now()));
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
  await p.evaluate(() => document.querySelector('#matBody .mini[data-grade]').click());
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
  chk('3 은 반 탭', await p.evaluate(() =>
    TABS.filter(t => document.getElementById('t-' + t).getAttribute('aria-selected') === 'true')[0]), 'cls');
  await p.keyboard.press('4');
  await p.waitForTimeout(200);
  chk('4 는 회차 탭', await p.evaluate(() =>
    TABS.filter(t => document.getElementById('t-' + t).getAttribute('aria-selected') === 'true')[0]), 'rnd');
  /* 머리가 두 줄이 되면서 탭이 열 개다. 하나만 켜지고 하나만 보여야 한다 —
     두 줄에서 각각 하나씩 켜지면 어느 화면을 보고 있는지 알 수 없다. */
  const only = await p.evaluate(() => {
    const out = [];
    for(const id of TABS){
      show(id);
      out.push([TABS.filter(t => document.getElementById('t-'+t).getAttribute('aria-selected')==='true').length,
                TABS.filter(t => document.getElementById('p-'+t).classList.contains('on')).length]);
    }
    show('dash');
    return out;
  });
  chk('언제나 한 탭만 켜진다', only.every(x => x[0]===1 && x[1]===1), true);
  chk('탭을 하나도 안 빼고 봤다', only.length, await p.evaluate(() => TABS.length));
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

  console.log('\n── DT 문자를 셸에서 바로 복사한다 ──');
  {
    /* 문구는 DT 의 pending.html 이 갖고 있고 셸은 **빌려 쓴다.** 이 저장소에는
       DT 가 없으므로(다른 저장소다) 그 화면을 흉내 내 세워 둔다. 여기서 볼 것은
       문구의 내용이 아니라 **빌리는 길이 실제로 이어지는가** 다 —
       문구 자체는 DT 저장소의 검사가 본다. */
    await p.evaluate(() => show('dash'));
    await p.waitForTimeout(600);

    const seen = await p.evaluate(() => ({
      dtCnt: (document.getElementById('pdCnt') || {}).textContent,
      pend: document.querySelectorAll('#pendList .row').length,
      pass: document.querySelectorAll('#passList .row').length,
      passShown: !document.getElementById('passWrap').hidden,
      btnPend: document.querySelectorAll('#pendList .mini.msg').length,
      btnPass: document.querySelectorAll('#passList .mini.msg').length,
      btnAbs: document.querySelectorAll('#absList .mini.msg').length,
    }));
    // 예전에는 여기가 undefined 였다(DT 가 객체로 주는데 배열로 알고 있었다)
    chk('DT 미완료 칸에 숫자가 찍힌다', seen.dtCnt, '1');
    chk('손이 필요한 것에 줄이 선다', seen.pend, 1);
    chk('통과한 학생이 보인다', [seen.passShown, seen.pass], [true, 1]);
    // 목록마다 세야 뜻이 있다. 통째로 세면 한 목록이 통째로 빠져도 안 걸린다.
    chk('세 목록에 문자 단추가 있다', [seen.btnPend, seen.btnPass, seen.btnAbs > 0], [1, 1, true]);

    const grab = async sel => {
      await p.click(sel);
      await p.waitForFunction(s => { const b = document.querySelector(s); return b && !b.disabled; },
                              sel, { timeout: 30000 });
      await p.waitForTimeout(200);
      return p.evaluate(() => navigator.clipboard.readText());
    };
    const one = await grab('#pendList .mini.msg');
    chk('재시 문자를 DT 에서 빌려 온다', one, '빌린재시:최예린/ch1/12/재시/1');
    const two = await grab('#passList .mini.msg');
    chk('통과 문자도 빌려 온다', two, '빌린통과:김지성/ch2/7/정시/1/96');

    /* 시험 미응시만 셸에 없어서 채점하다 말고 DT 로 넘어가야 했다.
       응시 주소까지 저쪽에서 빌린다 — 셸이 지어내면 경로가 바뀔 때 어긋난다. */
    const seenAbs = await p.evaluate(() => ({
      shown: !document.getElementById('absWrap').hidden,
      rows: document.querySelectorAll('#absList .row').length,
      cnt: (document.getElementById('abCnt') || {}).textContent,
    }));
    // 반 한 줄 + 학생 두 줄. 미응시 0명인 반은 아예 안 나온다
    chk('미응시 반과 학생이 선다', [seenAbs.shown, seenAbs.rows], [true, 3]);
    chk('미응시가 숫자 칸에도 뜬다', seenAbs.cnt, '2');
    const bc = await grab('#absList .mini.msg[data-stage="bc"]');
    chk('반 전체 공지를 빌려 온다', bc, '빌린미응시:반전체/ch1/12/빌린주소/ch1/12/bc');
    const one1 = await grab('#absList .mini.msg[data-stage="1"]');
    chk('개별 안내도 빌려 온다', one1, '빌린미응시:김도윤/ch1/12/빌린주소/ch1/12/1');
  }

  console.log('\n── 대답 안 하는 앱을 짚어 준다 ──');
  {
    const chips = await p.evaluate(() =>
      [].map.call(document.querySelectorAll('#connBar .conn'),
                  e => e.className.replace('conn ', '') + ':' + (e.querySelector('small') || {}).textContent));
    console.log('  ' + JSON.stringify(chips));
    // 창구를 늘리면 칸도 늘어야 한다. 숫자를 손으로 적어 두면 어긋난다.
    const want = await p.evaluate(() => CONN.length);
    chk('앱마다 한 칸씩 뜬다', chips.length, want);
    chk('다 정상이면 전부 ✓', chips.every(c => c.startsWith('ok')), true);

    /* 여기가 이 줄의 존재 이유다. DT 가 콜백을 무시하고 순수 JSON 을 주면
       — 실제로 한 해 내내 그랬다 — 화면에 '고장' 이라고 적혀야 한다. */
    const p2 = await ctx.newPage();
    await p2.route('**/macros/s/**', route => {
      const u = new URL(route.request().url());
      const cb = u.searchParams.get('callback'), act = u.searchParams.get('action');
      if (u.pathname.includes(DT_EP))            // DT: 콜백을 무시한다(옛 버그 재현)
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true, rows: [] }) });
      return route.fulfill({ status: 200, contentType: 'application/javascript',
        body: cb + '(' + JSON.stringify(act === 'all' ? { ok: true, n: 0, rows: [] } : { ok: true, students: [] }) + ')' });
    });
    await p2.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p2.waitForFunction(() => typeof EXAMS !== 'undefined' && EXAMS.length, null, { timeout: 20000 });
    /* 안 뜨면 그냥 실패로 적는다. 여기서 예외로 죽으면 남은 검사가 통째로
       안 돌고, 무엇이 문제인지도 안 보인다. */
    await p2.waitForFunction(() =>
      [].some.call(document.querySelectorAll('#connBar .conn'), e => e.classList.contains('bad')),
      null, { timeout: 30000 }).catch(() => {});
    const bad = await p2.evaluate(() =>
      [].filter.call(document.querySelectorAll('#connBar .conn'), e => e.classList.contains('bad'))
        .map(e => e.textContent.replace(/\s+/g, ' ')));
    console.log('  ' + JSON.stringify(bad));
    chk('대답 없는 DT 를 고장으로 적는다', bad.length > 0, true);
    chk('무엇이 안 되는지 이름을 적는다', bad.every(t => /DT/.test(t)), true);
    await p2.close();
  }

  console.log('\n── 요즘 반이 어려워하는 개념 ──');
  {
    await p.evaluate(() => show('dash'));
    await p.waitForTimeout(600);
    const mis = await p.evaluate(() => ({
      shown: !document.getElementById('misWrap').hidden,
      rows: [].map.call(document.querySelectorAll('#misList .row'),
        r => r.querySelector('.nm').textContent + ':' + r.querySelector('.cnt').textContent),
    }));
    chk('집계가 화면에 뜬다', mis.shown, true);
    // 두 학생이 걸린 것이 위, 한 명짜리가 아래
    chk('많이 걸린 것부터', mis.rows, ['몰농도:2명', '완충:1명']);
  }

  /* 여기부터는 앞의 검사들이 만들어 놓은 상태 위에서 돈다:
     명단 셋(김지성·새학생·이도현), 갈라진 이름표 하나, DT 흉내 응답. */
  const clip = async sel => {
    await p.click(sel);
    await p.waitForFunction(s => { const b = document.querySelector(s); return b && !b.disabled; },
                            sel, { timeout: 30000 });
    await p.waitForTimeout(250);
    return p.evaluate(() => navigator.clipboard.readText());
  };

  console.log('\n── 학생 카드 한 장에 세 앱이 모인다 ──');
  {
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('stu'); });
    await p.waitForTimeout(500);
    const roster = await p.evaluate(() => ROSTER.map(r =>
      r.name + '/' + (r.school || '—') + '/' + Object.keys(r.apps).sort().join('+')));
    console.log('  ' + JSON.stringify(roster));
    /* KMChC 시트에는 학교 열이 없다. 붙이는 장치는 처음부터 있었는데 셸이 그
       사실을 안 알려 줘서 한 번도 돌지 않았다 — 같은 아이가 두 줄로 떴고,
       어느 줄을 눌러도 기록이 반쪽이었다. 검사가 스스로 깃발을 세워 가려 놨다. */
    chk('KMChC 학생이 따로 뜨지 않는다', roster.length, 3);
    chk('한 줄에 두 앱이 모인다', roster[0], '김지성/휘문중/exam+km');

    await p.evaluate(() => document.querySelector('#stuList .row').click());
    await p.waitForTimeout(900);
    const other = await p.evaluate(() => ({
      titles: [].map.call(document.querySelectorAll('#stuOther .trk__i .trk__t'), e => e.textContent),
      kinds:  [].map.call(document.querySelectorAll('#stuOther .trk__i'), e => e.className.replace('trk__i ', '')),
      kmUrl:  (document.querySelector('#stuOther .trk__i.km .mini[data-url]') || { getAttribute: () => '' })
                .getAttribute('data-url'),
    }));
    console.log('  ' + JSON.stringify(other.titles));
    /* 여태 이 자리는 "DT 명단에도 있습니다" 한 줄이었다. 정작 물어보고 싶은
       것은 그쪽인데 — 통과했나, 재시가 밀렸나, 진단은 봤나. */
    chk('세 앱 기록이 한 카드에 선다', other.titles,
        ['DT 시험 미응시', 'DT 통과 · 96점', '화학 정밀 학습진단']);
    chk('급한 것이 위에 선다', other.kinds.map(k => k.replace(' sent','')), ['miss', 'pass', 'km']);
    /* 앞 화면(대시보드)에서 이 학생의 통과 문자를 이미 복사했다. 그 표시가
       학생 카드까지 따라와야 "보냈나?" 를 다시 세지 않는다. */
    chk('보낸 표시가 화면을 넘어 따라온다', other.kinds.filter(k => / sent/.test(k)), ['pass sent']);
    // 주소를 셸이 지어내면 저쪽이 경로를 바꾸는 날 조용히 어긋난다
    chk('설문 앱이 준 주소를 그대로 쓴다', other.kmUrl,
        'https://chemistreal.github.io/KMChC/report.html?id=k1');

    /* 이 한 줄이 syncWorkRows 의 존재 이유다. 대시보드와 카드가 서로 다르게
       잘라 담으면 여기서 **엉뚱한 학생 문구**가 나오고, 그대로 학부모에게 간다. */
    const msg = await clip('#stuOther .mini.msg[data-pass]');
    chk('카드에서 누른 문자가 그 학생 것이다', msg, '빌린통과:김지성/ch2/7/정시/1/96');
    const abs = await clip('#stuOther .mini.msg[data-abs][data-stage="1"]');
    chk('미응시 안내도 카드에서 바로', abs, '빌린미응시:김지성/ch1/12/빌린주소/ch1/12/1');
  }

  console.log('\n── 오늘 할 일을 한 줄에 세운다 ──');
  {
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(600);
    const jump = await p.evaluate(() => ({
      shown: !document.getElementById('jump').hidden,
      labels: [].map.call(document.querySelectorAll('#jump .chip'), e => e.textContent),
    }));
    console.log('  ' + JSON.stringify(jump.labels));
    chk('칩이 뜬다', jump.shown, true);
    // 반이 아니라 사람 수로 세야 "몇 명에게 보내야 하나" 가 된다
    chk('미응시는 사람 수로 센다', jump.labels[0], '시험 미응시2');
    chk('다섯 자리가 다 선다', jump.labels.length, 5);
    const jumped = await p.evaluate(() => {
      document.querySelector('#jump .chip[data-jump="passWrap"]').click();
      return document.getElementById('passWrap').classList.contains('flashed');
    });
    chk('누르면 그 자리를 짚어 준다', jumped, true);
  }

  console.log('\n── 오늘 못 하는 줄은 미룬다 ──');
  {
    /* 재시·미응시 목록에 오늘 손댈 수 없는 학생이 섞여 있으면 목록 전체를
       흘려보게 되고, 정말 오늘 해야 하는 줄까지 같이 흘러간다.
       지우면 안 된다 — 지운 것은 돌아오지 않는다. */
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(500);
    const before = await p.evaluate(() =>
      [].map.call(document.querySelectorAll('#absList .row.sub'), e => e.querySelector('.nm').textContent));
    chk('미응시 두 명이 서 있다', before, ['김도윤', '김지성']);

    const clicked = await p.evaluate(() => {
      const b = document.querySelector('#absList .row.sub .mini.snzb');
      if (!b) return false;
      b.click(); return true;
    });
    chk('미루기 단추가 있다', clicked, true);
    await p.waitForTimeout(900);

    const after = await p.evaluate(() => ({
      /* offsetParent 가 null 이면 화면에서 접힌 것이다. innerHTML 로 세면
         '지웠다' 와 '접었다' 를 구분하지 못한다 — 미루기는 지우는 것이 아니다. */
      seen: [].filter.call(document.querySelectorAll('#absList .row.sub'), e => e.offsetParent)
              .map(e => e.querySelector('.nm').textContent),
      kept: document.querySelectorAll('#absList .row.sub').length,
      bar:  (document.querySelector('#absList .snzbar') || { textContent: '' }).textContent.replace(/\s+/g, ' ').trim(),
      chip: (document.querySelector('#jump .chip[data-jump="absWrap"]') || { textContent: '' }).textContent,
      /* 숫자 카드는 반 상태다. 미뤘다고 미응시가 한 명 줄어드는 것은 아니다 —
         줄이면 "학생이 시험을 봤다" 로 읽힌다. */
      card: (document.getElementById('abCnt') || { textContent: '' }).textContent,
    }));
    console.log('  ' + JSON.stringify(after.seen) + ' · ' + after.bar);
    chk('미룬 줄은 눈에서 내려간다', after.seen, ['김지성']);
    chk('지운 것이 아니라 접은 것이다', after.kept, 2);
    chk('몇을 미뤘는지 말해 준다', /미룬 것 1명/.test(after.bar), true);
    /* 오늘 할 일에서는 빠져야 한다 — 그게 미루기의 전부다. */
    chk('오늘 할 일에서 빠진다', after.chip, '시험 미응시1');
    /* 반 상태에서까지 빼면 학생이 사라진 것처럼 보인다. 넣되 적는다
       (그림 쪽 '미룬 N명 포함' 은 명단이 있어야 그려지므로 tests/hub.js 가 본다). */
    chk('반 상태 숫자는 그대로다', after.card, '2');

    const shown = await p.evaluate(() => {
      document.querySelector('#absList .snzbar .mini[data-snzshow]').click();
      return [].filter.call(document.querySelectorAll('#absList .row.sub'), e => e.offsetParent)
               .map(e => e.querySelector('.nm').textContent);
    });
    chk('펼치면 다시 보인다', shown, ['김도윤', '김지성']);

    /* 잘못 눌렀으면 그 자리에서 무를 수 있어야 한다. 미루기는 되돌릴 수 있는
       일이라 확인창을 세우는 것보다 이쪽이 낫다. */
    const undone = await p.evaluate(() => {
      const b = document.querySelector('#absList .row.sub .mini[data-snz][data-off]');
      if (!b) return null;
      b.click(); return true;
    });
    chk('지금 보기 단추가 있다', undone, true);
    await p.waitForTimeout(900);
    const back = await p.evaluate(() => ({
      seen: [].filter.call(document.querySelectorAll('#absList .row.sub'), e => e.offsetParent)
              .map(e => e.querySelector('.nm').textContent),
      chip: (document.querySelector('#jump .chip[data-jump="absWrap"]') || { textContent: '' }).textContent,
      bar:  !!document.querySelector('#absList .snzbar'),
    }));
    chk('무르면 도로 올라온다', back.seen, ['김도윤', '김지성']);
    chk('오늘 할 일에도 도로 잡힌다', back.chip, '시험 미응시2');
    chk('미룬 것이 없으면 줄도 사라진다', back.bar, false);
  }

  console.log('\n── 학생을 걸러 본다 ──');
  {
    await p.evaluate(() => show('stu'));
    await p.waitForTimeout(400);
    const counts = await p.evaluate(() =>
      [].map.call(document.querySelectorAll('#stuFilter .chip'), e => e.textContent));
    console.log('  ' + JSON.stringify(counts));
    chk('칩마다 몇 명인지 적는다', counts, ['전체3', '파이널3', 'DT0', '학습진단1', '파이널 기록 없음0']);
    const km = await p.evaluate(() => {
      document.querySelector('#stuFilter .chip[data-stuf="km"]').click();
      return { n: document.querySelectorAll('#stuList .row').length,
               on: document.querySelector('#stuFilter .chip[data-stuf="km"]').getAttribute('aria-pressed') };
    });
    chk('고른 것만 남는다', [km.n, km.on], [1, 'true']);
    // 아무도 없을 때 '찾는 학생이 없습니다' 라고 하면 검색이 잘못된 줄 안다
    const none = await p.evaluate(() => {
      document.querySelector('#stuFilter .chip[data-stuf="noexam"]').click();
      return document.getElementById('stuList').textContent.trim();
    });
    chk('비면 조건 때문이라고 말한다', none, '이 조건에 맞는 학생이 없습니다.');
    await p.evaluate(() => document.querySelector('#stuFilter .chip[data-stuf="all"]').click());
  }

  console.log('\n── 회차에서 바로 들고 나간다 ──');
  {
    await p.evaluate(() => { show('rnd'); openRound('jmchc-2'); });
    await p.waitForTimeout(400);
    const tsv = await clip('#dlgBody .mini[data-rnd="table"]');
    const lines = tsv.split('\n');
    console.log('  ' + JSON.stringify(lines[0]));
    chk('엑셀 머리글이 탭으로 나뉜다', lines[0], '이름\t학교\t맞은 문항\t총 문항\t정답률(%)');
    chk('본 학생 수만큼 줄이 선다', lines.length - 1,
        await p.evaluate(() => RND_OPEN.rows.length));
    chk('이름·학교가 들어간다', /김지성\t휘문중\t\d+\t\d+\t\d+/.test(lines[1]), true);

    /* 화면은 120명만 보여 준다. 복사까지 잘리면 공지에서 아이가 빠지는데,
       빠진 줄도 모른다. */
    const names = await clip('#dlgBody .mini[data-rnd="names"]');
    console.log('  ' + JSON.stringify(names));
    chk('안 본 학생 이름이 공지에 붙는 모양으로', names, '새학생, 이도현');
    await p.evaluate(() => document.getElementById('dlg').close());
    chk('닫으면 회차를 놓는다', await p.evaluate(() => RND_OPEN), null);
  }

  console.log('\n── 자료는 실제로 있는 것만 건다 ──');
  {
    /* 화학Ⅱ 는 문제지·OMR 이 18회까지 있는데 해설 HTML 은 7회까지뿐이다.
       회차 번호로 주소를 지어내면 눌러 본 뒤에야 404 를 만난다. */
    await p.evaluate(() => show('mat'));
    await p.waitForTimeout(500);
    const chips = await p.evaluate(() =>
      [].map.call(document.querySelectorAll('#matTabs .chip'), e => e.textContent));
    console.log('  ' + JSON.stringify(chips));
    chk('갈래가 여섯', chips.length, 6);
    chk('파이널이 먼저', /^파이널 모의고사/.test(chips[0]), true);

    const ch2 = await p.evaluate(async () => {
      document.querySelector('#matTabs .chip[data-mat="ch2"]').click();
      await new Promise(r => setTimeout(r, 400));
      const rows = [].map.call(document.querySelectorAll('#matBody tbody tr'), tr => {
        const td = tr.querySelectorAll('td');
        return { name: td[0].textContent,
                 dots: [].map.call(td[1].querySelectorAll('.dot'), d => d.className.replace('dot', '').trim()),
                 haeseol: td[3].textContent.trim(),
                 links: [].map.call(td[3].querySelectorAll('a'), a => a.getAttribute('href')) };
      });
      return rows;
    });
    console.log('  ' + JSON.stringify(ch2));
    chk('화학Ⅱ 두 회차', ch2.map(r => r.name), ['화학Ⅱ 1회', '화학Ⅱ 12회']);
    /* 12회는 해설 HTML 이 없다. 점은 '반쯤' 이고, 링크는 PDF 하나뿐이며,
       있지도 않은 haeseol_ch2_round12.html 은 어디에도 없어야 한다. */
    chk('해설이 PDF 뿐이면 점을 반만 켠다', ch2[1].dots[1], 'half');
    chk('있는 것만 건다', ch2[1].links, ['../DT/haeseol_ch2_round12.pdf']);
    chk('없는 주소를 지어내지 않는다',
        /haeseol_ch2_round12\.html/.test(await p.content()), false);

    /* 강의 목차는 목차 페이지가 원본이다. 베껴 두면 강의가 늘 때 갈라진다. */
    const lec = await p.evaluate(async () => {
      document.querySelector('#matTabs .chip[data-mat="lec"]').click();
      await new Promise(r => setTimeout(r, 900));
      return { n: document.querySelectorAll('#matBody tbody tr').length,
               first: (document.querySelector('#matBody tbody tr td:nth-child(2)') || {}).textContent };
    });
    console.log('  강의 ' + lec.n + '개 · 첫 강의 ' + JSON.stringify(lec.first));
    chk('강의를 목차에서 읽어 온다', lec.n > 100, true);
    const tool = await p.evaluate(async () => {
      document.querySelector('#matTabs .chip[data-mat="tool"]').click();
      await new Promise(r => setTimeout(r, 300));
      return [].map.call(document.querySelectorAll('#matBody .row .mini'), a => a.getAttribute('href'));
    });
    chk('도구가 열린다', tool.length >= 15, true);
    chk('도구는 모두 주소가 있다', tool.every(h => !!h), true);
    await p.evaluate(() => document.querySelector('#matTabs .chip[data-mat="final"]').click());
  }

  /* ── 반 탭과 잠금은 상태가 달라야 보인다 ────────────────────────────
     앞 검사들은 DT 반 명단을 **비워** 두고 돈다(학생을 보태면 명단·회차 검사가
     흔들린다). 반 탭은 반이 있어야 보이므로 창을 따로 연다. */
  console.log('\n── 반으로도 물을 수 있다 ──');
  {
    const p3 = await ctx.newPage();
    const errs3 = [];
    p3.on('pageerror', e => errs3.push(String(e)));
    await p3.route('**/DT/pending.html', route => route.fulfill({
      status: 200, contentType: 'text/html; charset=utf-8',
      body: '<!doctype html><meta charset="utf-8"><script>'
          + 'function shareMsg(d,s){ return "재시:"+d.name; }'
          + 'function passMsg(d){ return "통과:"+d.name; }'
          + 'function examLink(c,r){ return "L/"+c+"/"+r; }'
          + 'function absentMsg(d,s){ return "미응시:"+(d.name||"반전체")+"/"+s; }'
          + '</script>',
    }));
    await p3.route('**/macros/s/**', route => {
      const u = new URL(route.request().url());
      const cb = u.searchParams.get('callback'), act = u.searchParams.get('action');
      const isDT = u.pathname.includes(DT_EP);
      const body = (isDT && act === 'names') ? { ok: true, classes: [
            { label:'화학1 토1:30', course:'ch1', students:[
              {name:'가',school:'A중',year:'2'},{name:'나',school:'A중',year:'2'},
              {name:'다',school:'A중',year:'2'},{name:'라',school:'A중',year:'2'}] },
            { label:'화학2 일6-10', course:'ch2', students:[{name:'마',school:'B중',year:'3'}] }] }
        : act === 'names' ? { ok: true, students: [] }
        : act === 'pending' ? { ok: true, pending: { stale: [], active: [
            { studentKey:'k', name:'나', school:'A중', course:'ch1', round:12,
              lastAttempt:'정시', nextNeeded:'재시', score:55, days:3 }] } }
        : act === 'passed' ? { ok: true, passed: { passed: [
            { name:'다', school:'A중', course:'ch1', round:12, attempt:'정시', tries:1, score:92, date:'8/1' }] } }
        : act === 'absentees' ? { ok: true, absentees: { classes: [
            { label:'화학1 토1:30', course:'ch1', round:12, total:4, present:2, absent:['가','나'] }] } }
        : { ok: true, rows: [] };
      return route.fulfill({ status: 200, contentType: 'application/javascript',
                             body: cb + '(' + JSON.stringify(body) + ')' });
    });
    /* 열쇠칸은 오리진 하나에 하나뿐이라, 앞에서 넣어 둔 것이 이 창에도 남아
       있다. 잠금을 보려면 먼저 비운다(같은 오리진의 아무 화면에서나 지운다). */
    await p3.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'domcontentloaded' });
    await p3.evaluate(() => localStorage.removeItem('chemistreal:gate'));
    await p3.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p3.waitForTimeout(400);
    /* 이 창은 열쇠칸이 비어 있다 — 먼저 잠금이 뜨는지 본다. */
    chk('처음 들어오면 코드를 묻는다', await p3.evaluate(() => !!document.getElementById('gate')), true);
    chk('잠긴 동안에는 창구를 안 부른다',
        await p3.evaluate(() => document.querySelectorAll('#connBar .conn').length), 0);
    await p3.fill('#gateIn', '1234');
    await p3.click('#gateGo');
    chk('틀린 코드로는 안 열린다', await p3.evaluate(() => !!document.getElementById('gate')), true);
    await p3.fill('#gateIn', '0000');
    await p3.click('#gateGo');
    await p3.waitForTimeout(2200);
    chk('맞히면 열린다', await p3.evaluate(() => !!document.getElementById('gate')), false);
    chk('열리면 그제야 부른다',
        await p3.evaluate(() => document.querySelectorAll('#connBar .conn').length > 0), true);

    await p3.evaluate(() => show('cls'));
    await p3.waitForTimeout(600);
    const cls = await p3.evaluate(() => ({
      tabs: [].map.call(document.querySelectorAll('#clsTabs .chip'), e => e.textContent),
      rows: [].map.call(document.querySelectorAll('#clsList .row'), r => [
        r.querySelector('.nm').textContent, r.querySelector('.tag').textContent]),
      legend: [].map.call(document.querySelectorAll('#clsHead .legend span'), e => e.textContent),
      donut: (document.querySelector('#clsHead .donut span') || {}).textContent,
      bars: document.querySelectorAll('#clsHead .stack i').length,
    }));
    console.log('  ' + JSON.stringify(cls.tabs) + ' ' + JSON.stringify(cls.rows));
    chk('반마다 칩 하나', cls.tabs.length, 2);
    /* '나' 는 미응시이면서 재시 대기다. 상태는 하나로 정해지므로 **한 명으로**
       센다 — 두 번 세면 반 인원보다 큰 숫자가 나와 아무 뜻이 없다. */
    chk('손이 필요한 사람을 한 번만 센다', /손 2/.test(cls.tabs[0]), true);
    /* '나' 는 미응시이면서 재시 대기다. 지금 손이 필요한 쪽을 말해야 한다. */
    chk('상태는 급한 것이 이긴다', cls.rows,
        [['가','미응시'],['나','미응시'],['다','통과'],['라','아직']]);
    chk('막대는 있는 칸만 그린다', cls.bars, 3);
    chk('범례가 색마다 이름을 붙인다', cls.legend, ['미응시 2','통과 1','아직 1']);
    chk('통과 비율을 도넛으로', cls.donut, '25%');

    /* 반에서 바로 문자. 문구는 여기서도 DT 에서 빌린다. */
    await p3.click('#clsList .row .mini.msg');
    await p3.waitForFunction(() => {
      const b = document.querySelector('#clsList .row .mini.msg'); return b && !b.disabled; },
      null, { timeout: 30000 });
    await p3.waitForTimeout(250);
    chk('반에서 문자를 바로 복사한다',
        await p3.evaluate(() => navigator.clipboard.readText()), '미응시:가/1');
    const names = await p3.evaluate(async () => {
      document.querySelector('#clsHead .mini[data-clsact="names"]').click();
      await new Promise(r => setTimeout(r, 250));
      return navigator.clipboard.readText();
    });
    chk('반 명단을 그대로 복사한다', names, '가, 나, 다, 라');

    const other = await p3.evaluate(async () => {
      [].filter.call(document.querySelectorAll('#clsTabs .chip'),
                     c => /화학2/.test(c.textContent))[0].click();
      await new Promise(r => setTimeout(r, 300));
      return [].map.call(document.querySelectorAll('#clsList .row .nm'), e => e.textContent);
    });
    chk('반을 바꾸면 그 반이 나온다', other, ['마']);

    /* DT 의 두 화면을 탭으로 얹는다. 재시·문자 화면은 어차피 문구를 빌리려고
       띄우던 것이라, 두 장이 뜨면 앱스크립트를 두 번 두드린다. */
    await p3.evaluate(() => { show('dtp'); show('dtr'); });
    await p3.waitForTimeout(1200);
    const frames = await p3.evaluate(() => ({
      dtp: document.querySelectorAll('#p-dtp iframe').length,
      dtr: document.querySelectorAll('#p-dtr iframe').length,
      stray: document.querySelectorAll('body > iframe').length,
      src: (document.querySelector('#p-dtr iframe') || {}).getAttribute
        ? document.querySelector('#p-dtr iframe').getAttribute('src') : '',
    }));
    chk('두 화면이 탭으로 뜬다', [frames.dtp, frames.dtr], [1, 1]);
    chk('몰래 한 장 더 뜨지 않는다', frames.stray, 0);
    chk('명단 화면은 DT 것을 그대로', frames.src, '../DT/roster.html');
    chk('반 창에도 예외가 없다', errs3.filter(e => !/Failed to fetch|ERR_/.test(e)), []);
    await p3.close();
  }

  chk('콘솔에 예외가 없다', errs.filter(e => !/Failed to fetch|ERR_/.test(e)), []);
  await b.close();
  console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
  process.exit(fail ? 1 : 0);
})();
