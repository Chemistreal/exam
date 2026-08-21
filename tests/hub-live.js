/* ============================================================
   통합 셸 · 실제 브라우저 회귀 테스트
   (⚠ 예전에는 'playwright 가 없으면 저절로 건너뛴다' 고 적혀 있었다. 판에서는
    REQUIRE_BROWSER=1 이라 **건너뛰지 않고 빨간불**이다 — 건너뛴 것은 초록이 아니다)
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
/* 멈추는 검사는 실패하는 검사보다 나쁘다 — tests/_watchdog.js 주석 참고. */
require('./_watchdog.js')(240);
/* 검사가 진짜 시트에 쓰면 안 된다. 실제로 CI 가 돌 때마다 파이널 앱이
   진짜 앱스크립트로 제출해서, 홍길동·예비본 같은 줄이 학생들 석차
   모집단에 섞여 들어갔다. 브라우저를 띄우자마자 그 길을 끊는다. */
const seal = require('./_seal.js');
const noSheet = require('./_nosheet.js');
let chromium;
try { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')); }
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

const PORT = Number(process.env.PORT || 8931);
let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* ── 기다리는 법 ──────────────────────────────────────────────────────
   "이쯤이면 다 됐겠지" 하고 재우면 빠른 기계에서는 낭비고 느린 기계에서는
   실패다. 한때 이 파일에만 고정 대기가 여든아홉 군데, 합쳐 46초였다 — CI 가
   이따금 까닭 없이 빨간불이던 뿌리가 여기다. 코드는 그대로인데 검사가
   흔들리면 사람은 빨간불을 믿지 않게 되고, 그러면 진짜 고장도 같이 묻힌다.

   두 가지로 바꾼다.

   until    조건이 참이 될 때까지만 기다린다. 언제 참이 되는지 아는 자리에.
   settled  값이 **더 이상 안 바뀔 때까지** 기다린다. 언제 끝나는지 모르는
            자리에. 기대값으로 기다리면 안 된다 — 두 줄을 기대하면서 두 줄이
            될 때까지 기다리면 '두 줄인가' 는 언제나 참이 되어, 검사가 스스로
            답을 맞춰 주는 꼴이 된다.

   지치면 무엇을 기다렸는지 적고 실패시킨다. 조용히 넘어가면 그다음 검사가
   엉뚱한 자리에서 깨져 원인을 못 찾는다. */
async function until(p, label, fn, arg, ms) {
  try { await p.waitForFunction(fn, arg, { timeout: ms || 15000, polling: 50 }); return true; }
  catch (e) { console.log('  FAIL  기다리다 지쳤다: ' + label); fail++; return false; }
}
async function settled(p, label, fn, arg, ms) {
  const t0 = Date.now(), max = ms || 15000;
  let prev = '\u0000<아직>', same = 0;   // 어떤 값과도 같지 않은 첫 표식
  while (Date.now() - t0 < max) {
    let cur;
    try { cur = JSON.stringify(await p.evaluate(fn, arg)); } catch (e) { cur = '\u0000<읽히지않음>'; }
    same = (cur === prev) ? same + 1 : 0;
    prev = cur;
    /* 여섯 번(≈360ms) 잇달아 같으면 다 그려진 것으로 본다. 짧게 잡으면 응답이
       띄엄띄엄 오는 화면에서 그 틈을 '끝났다' 로 잘못 읽는다. */
    if (same >= 6) return true;
    await p.waitForTimeout(60);
  }
  console.log('  FAIL  끝내 안 멎었다: ' + label);
  fail++;
  return false;
}

(async () => {
  const b = seal(await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox'] }));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(b);
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
                   { id: 'k1', name: '김마루', grade: '중2', kind: '실제',
                     link: 'https://chemistreal.github.io/KMChC/report.html?id=k1', ts: 0 } ] }
               /* DT 가 실제로 주는 모양이다 — {active, stale, …} 객체. 배열로
                  흉내 내면 'DT 미완료' 가 undefined 로 찍히던 버그를 못 잡는다. */
               : act === 'pending' ? { ok: true, pending: { activeDays: 14, generatedAt: 'T', stale: [], active: [
                   { studentKey: 's1', name: '최나래', school: '역삼중', year: '2', course: 'ch1', round: 12,
                     lastAttempt: '정시', nextNeeded: '재시', score: 68, days: 9, lastDate: '6/17',
                     reportLink: 'https://x/report.html?student=a', active: true } ] } }
               /* 통과·미응시를 **파이널에도 있는 학생**(김마루)으로 둔다. 학생 카드가
                  세 앱을 한 장에 모으는지 보려면 같은 아이여야 한다. 학교는 일부러
                  짧게 준다 — DT 는 실제로 '휘문' 과 '휘문중' 을 섞어서 준다. */
               : act === 'passed' ? { ok: true, passed: { days: 14, generatedAt: 'T', passed: [
                   { name: '김마루', school: '휘문', year: '2', course: 'ch2', round: 7, attempt: '정시',
                     tries: 1, score: 96, date: '6/19', days: 1, reportLink: 'https://x/report.html?student=b' } ] } }
               : act === 'absentees' ? { ok: true, absentees: { generatedAt: 'T', classes: [
                   { label: '화학1 토1:30-5:30', course: 'ch1', round: 12, total: 8, present: 6, absent: ['김도윤', '김마루'] },
                   { label: '화학2 일6-10', course: 'ch2', round: 7, total: 6, present: 6, absent: [] } ] } }
               /* 이름이 붙은 오개념. 익명본(cohortmis)과 같은 개념을 다루되
                  이쪽은 사람이 보인다 — '몰농도 7명' 다음에 할 일이 있으려면
                  누구인지가 있어야 한다. 김마루은 **두 줄**로 준다(회차가 다름):
                  한 사람이 둘로 서면 보충 인원이 부푼다. */
               /* 넛지가 서려면 '보냈다' 와 '열어 봤다' 가 둘 다 있어야 한다.
                  김마루은 닷새 전에 보냈는데 그 뒤로 안 열었고, 최나래은
                  아예 안 보낸 채 오래 밀렸다. */
               : act === 'sentlog' ? { ok: true, sent: [
                   { kind:'pass', name:'김마루', course:'ch2', round:7,
                     ts: now - 5 * D, at:'6/19 10:00' } ] }
               : act === 'views' ? { ok: true, views: [
                   { studentKey:'s9', name:'다른학생', school:'X중', ts: now - 1 * D, at:'', n:1 } ] }
               : act === 'mistags' ? { ok: true, mis: { days: 21, rows: [
                   { name: '김마루', school: '휘문중', course: 'ch2', round: 12, attempt: '재시',
                     /* ⚠ days 5 는 일부러다. 최나래(3일)보다 **덜 최근**이라,
                        최근 순으로만 세우면 김마루이 아래로 내려간다.
                        되풀이(2회차)를 먼저 세우는지 여기서 갈린다. */
                     pass: true, score: 96, days: 5, tags: ['몰농도', '완충'],
                     reportLink: 'https://x/report.html?student=b' },
                   /* 7회는 위 자료 목록에 **없다.** 주소를 지어내면 404 로 끝난다. */
                   { name: '김마루', school: '휘문', course: 'ch2', round: 7, attempt: '정시',
                     pass: false, score: 61, days: 9, tags: ['몰농도'],
                     reportLink: 'https://x/report.html?student=b2' },
                   { name: '최나래', school: '역삼중', course: 'ch1', round: 1, attempt: '정시',
                     pass: false, score: 68, days: 3, tags: ['몰농도'],
                     reportLink: 'https://x/report.html?student=a' },
                   { name: '김도윤', school: '', course: 'ch1', round: 1, attempt: '정시',
                     pass: false, score: 40, days: 2, tags: ['완충'], reportLink: '' } ] } }
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
      a1: put('jmchc-1', '김마루', '휘문중', 45, now - D),
      b1: put('jmchc-1', '이아람', '대원국제중', 20, now - D + 1000),
      a2: put('jmchc-2', '김마루', '휘문중', 50, now),
    };
  });

  /* networkidle 은 쓰지 않는다 — 셸이 시트·DT 를 부르므로 영영 조용해지지 않는다. */
  await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => typeof EXAMS !== 'undefined' && EXAMS.length, null, { timeout: 20000 });

  console.log('── 회차 표가 기록과 맞는다 ──');
  await p.evaluate(() => show('rnd'));
  await settled(p, '회차 표가 다 그려진다',
    () => document.querySelectorAll('#rndTable tbody tr').length);
  const rnd = await p.evaluate(() => [].map.call(document.querySelectorAll('#rndTable tbody tr'),
    r => [].map.call(r.querySelectorAll('td'), td => td.textContent)));
  chk('회차 두 줄', rnd.length, 2);
  chk('최근 채점한 회차가 위에', rnd[0][0], 'JMChC 모의고사 2회');
  chk('1회는 두 명', rnd[1][1], '2');
  chk('내부 이름이 새지 않는다', /jmchc/.test(rnd.map(r => r[0]).join(' ')), false);
  /* ── 없는 것을 없다고 말한다 ────────────────────────────────────
     이 표는 **채점 기록이 있는 회차만** 세운다. 그런데 시험은 서른아홉 회차가
     있고, 기록이 없는 회차는 조용히 빠졌다 — "화올 2011 은 왜 없지" 를 알
     길이 없었다. 몇 개가 빠졌는지 적는다. */
  const 빠짐 = await p.evaluate(() => ({
    글: ((document.getElementById('rndNote') || {}).innerText || '').replace(/\s+/g, ' ').trim(),
    선회차: document.querySelectorAll('#rndTable tbody tr').length,
    전체: (typeof EXAMS !== 'undefined' && EXAMS.length) || 0,
  }));
  console.log('  ' + 빠짐.글);
  chk('기록이 있는 회차 수를 적는다', 빠짐.글.includes(빠짐.선회차 + '회차'), true);
  chk('기록이 없는 회차 수도 적는다',
      빠짐.글.includes((빠짐.전체 - 빠짐.선회차) + '회차'), true);
  chk('어디로 가야 하는지도 적는다', /자료/.test(빠짐.글), true);

  console.log('\n── 성적표를 열어도 기록이 늘지 않는다 ──');
  const before = await p.evaluate(() => ({
    n1: JSON.parse(localStorage.getItem('final:roster:jmchc-1') || '[]').length,
    raw: localStorage.getItem('final:roster:jmchc-1'),
  }));
  await p.evaluate(() => { show('stu'); });
  await until(p, '학생 목록이 뜬다', () => !!document.querySelector('#stuList .row'));
  await p.evaluate(() => document.querySelector('#stuList .row').click());
  await until(p, '학생 카드가 다 찬다',
    () => !!document.getElementById('dlgName') &&
          !!document.getElementById('dlgName').textContent.trim() &&
          document.querySelectorAll('#dlgBody .cards .card b').length > 0);
  const card = await p.evaluate(() => ({
    name: document.getElementById('dlgName').textContent,
    stats: [].map.call(document.querySelectorAll('#dlgBody .cards .card b'), x => x.textContent),
    acts: document.querySelectorAll('#dlgBody .mini[data-act]').length,
    spark: document.querySelectorAll('#dlgBody .spark i').length,
  }));
  chk('학생 카드가 열린다', card.name, '김마루');
  chk('응시 · 평균 · 최고 · 최근', card.stats.length, 4);
  chk('두 회차 모두 단추가 있다', card.acts, 4);
  chk('추세가 그려진다', card.spark, 2);

  await p.evaluate(() => document.querySelector('#dlgBody .mini[data-act="open"]').click());
  /* 여기서 '성적표가 떴는가' 로 기다리면 안 된다. 바로 다음 줄이 재는 것이
     **뜬 뒤에 파이널의 hashchange 가 덮지 않는가** 라, 뜨자마자 통과시키면
     덮이는 순간을 놓친다. 화면이 멎을 때까지 기다린 뒤에 본다. */
  await settled(p, '연 성적표 화면이 멎는다', () => {
    const f = document.querySelector('#p-exam iframe');
    if (!f || !f.contentDocument) return null;
    const a = f.contentDocument.getElementById('app');
    return [f.contentWindow.location.hash.slice(0, 12), a ? a.innerText.length : 0];
  }, null, 20000);
  const opened = await p.evaluate(() => {
    const f = document.querySelector('#p-exam iframe');
    return {
      tab: document.getElementById('t-exam').getAttribute('aria-selected'),
      /* ⚠ 앞을 12자만 떼면 안 된다. 해시 앞에 또래 통계(`s=`)와 채점일(`t=`)이
         붙을 수 있어서 `#t=20260811&r=jmchc-…` 이 된다 — 12자면 `r=` 가
         잘려 나간다. 셸은 규칙을 베끼지 않고 파이널의 shareLinkFinal 을
         빌리므로, **저쪽이 자라면 이 자가 먼저 운다.** 넉넉히 뗀다. */
      hash: f ? f.contentWindow.location.hash.slice(0, 60) : '',
      text: f ? (f.contentDocument.getElementById('app') || { innerText: '' }).innerText.replace(/\s+/g, ' ') : '',
    };
  });
  chk('파이널 탭으로 넘어간다', opened.tab, 'true');
  chk('성적표 주소로 간다', /[#&]r=jmchc-/.test(opened.hash), true);
  /* 파이널의 hashchange 가 우리가 연 화면을 덮으면 시험 목록이 뜬다 */
  chk('연 화면이 덮이지 않는다', /성적표|핵심 진단/.test(opened.text), true);
  chk('그 학생 이름이 성적표에 있다', /김마루/.test(opened.text), true);

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
  /* ⚠ `r=` 앞에 붙는 칸을 **하나하나 적어 두면** 칸이 늘 때마다 이 자가 운다.
     실제로 채점일(`t=`)을 들이자마자 여기가 빨간불이었다. 규칙은 하나다 —
     `r=` 앞에 `이름=값&` 이 몇 개든 올 수 있다. 그 모양을 본다. */
  chk('성적표 주소 모양이다',
      /final\.html#([a-z]+=[^&]*&)*r=jmchc-1\./.test(link.mine), true);

  console.log('\n── 자료에서 채점으로 바로 ──');
  await p.evaluate(() => show('mat'));
  await until(p, '자료 목록이 뜬다', () => !!document.querySelector('#matBody .mini[data-grade]'));
  await p.evaluate(() => document.querySelector('#matBody .mini[data-grade]').click());
  await settled(p, '채점 화면이 멎는다', () => {
    const f = document.querySelector('#p-exam iframe');
    if (!f || !f.contentDocument) return null;
    const h = f.contentDocument.querySelector('h2');
    return [f.contentDocument.querySelectorAll('.omr-grid .ansin').length, h ? h.textContent : ''];
  }, null, 20000);
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
    (document.querySelector('#qqList .row .nm') || { textContent: '' }).textContent), '김마루');

  console.log('\n── 채점하는 순간 스스로 따라온다 ──');
  {
    /* 여기가 이 파일의 존재 이유다. iframe 안에서 저장한 것이 부모에게
       storage 이벤트로 오는지는 띄워 봐야만 안다. 안 오면 셸의 숫자는
       새로고침 전까지 거짓말을 한다 — 채점하는 날 내내. */
    await p.evaluate(() => show('dash'));
    await settled(p, '대시보드 숫자가 멎는다',
      () => (document.getElementById('todayCnt') || {}).textContent);
    const before = await p.evaluate(() =>
      (document.getElementById('todayCnt') || {}).textContent);

    await p.evaluate(() => show('exam'));
    /* 파이널이 iframe 안에서 다 뜰 때까지. 밖에서 부를 함수가 생겼는지로 안다 —
       'iframe 이 있는가' 로는 껍데기만 보고 지나간다. */
    await until(p, '파이널이 iframe 안에 다 뜬다', () => {
      const f = document.querySelector('#p-exam iframe');
      return !!(f && f.contentWindow && typeof f.contentWindow.openExam === 'function'
                && f.contentDocument && f.contentDocument.getElementById('nm'));
    }, null, 30000);
    await p.evaluate(() => {
      const f = document.querySelector('#p-exam iframe'), w = f.contentWindow, d = f.contentDocument;
      w.openExam('jmchc-5');
      d.getElementById('nm').value = '새학생'; d.getElementById('sch').value = 'Z중';
      for (let q = 1; q <= 60; q++) w.setAns(q, 1);
      w.scoreAuto();
    });
    /* storage 이벤트가 건너오기를 기다린다. 안 건너오면 여기서 '기다리다
       지쳤다' 로 멎는데, 그것이 곧 이 검사가 잡으려는 고장이다 — 고정 시간을
       재고 지나가는 것보다 정확하고, 빠른 기계에서 헛되이 기다리지도 않는다. */
    await until(p, '채점이 셸의 숫자로 건너온다', (b) =>
      (document.getElementById('todayCnt') || {}).textContent !== b, before, 20000);
    /* 대시보드 탭으로 가지도 않았는데 이미 바뀌어 있어야 한다.
       ⚠ 자리 번호(첫 칸)로 짚지 않는다. 카드 차례를 바꾸는 날 조용히 엉뚱한
         칸을 보게 된다 — 실제로 그랬다(급한 것을 앞으로 옮기니 첫 칸이
         '시험 미응시' 가 됐다). 이름표로 짚는다. */
    const after = await p.evaluate(() =>
      (document.getElementById('todayCnt') || {}).textContent);
    chk('대시보드로 가지 않아도 숫자가 바뀐다', Number(after) > Number(before), true);

    await p.evaluate(() => show('rnd'));
    await settled(p, '회차 표가 다시 멎는다',
      () => document.querySelectorAll('#rndTable tbody tr').length);
    chk('회차 표에도 새 회차가 늘었다', await p.evaluate(() =>
      [].some.call(document.querySelectorAll('#rndTable tbody tr td:first-child'),
        td => /5회/.test(td.textContent))), true);
  }

  console.log('\n── 갈라진 이름을 셸이 짚어 준다 ──');
  {
    await p.evaluate(() => {
      // 같은 학생을 '김 마루' 으로 한 번 더 저장한다(파이널 앱이 쓰는 형식 그대로)
      const arr = JSON.parse(localStorage.getItem('final:roster:jmchc-2'));
      const r = arr[0];
      arr.push(Object.assign({}, r, { name: '김 마루', ts: r.ts + 1000 }));
      localStorage.setItem('final:roster:jmchc-2', JSON.stringify(arr));
      refreshLocal();
    });
    await p.waitForTimeout(400);
    chk('합쳐야 할 이름에 뜬다', await p.evaluate(() =>
      !document.getElementById('mergeWrap').hidden), true);
    chk('두 이름표를 다 적는다', await p.evaluate(() => {
      const t = (document.querySelector('#mergeList .row') || { textContent: '' }).textContent;
      return /김마루/.test(t) && /김 마루/.test(t);
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

  console.log('\n── 안 한 것이 떠오르게 (넛지) ──');
  {
    /* 미루기는 선생님이 **누른** 것만 미룬다. 잊은 것은 대개 누른 적이 없다. */
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(900);
    const n0 = await p.evaluate(() => ({
      shown: !document.getElementById('nudge').hidden,
      rows: [].map.call(document.querySelectorAll('#nudge .ndg'), e => [
        e.querySelector('.kindl').textContent, e.querySelector('.who').textContent]),
      why: [].map.call(document.querySelectorAll('#nudge .why'), e => e.textContent),
    }));
    console.log('  ' + JSON.stringify(n0.rows));
    chk('넛지가 뜬다', n0.shown, true);
    /* 닷새 전에 통과 문자를 보냈는데 그 학생은 성적표를 안 열었다. 다른 학생만
       열었다 — 이름으로 맞추지 않으면 '누군가 열었으니 됐다' 가 된다. */
    chk('보냈는데 안 열어 본 사람을 짚는다',
        n0.rows.some(r => r[0] === '안 열어 봄' && r[1] === '김마루'), true);
    /* 재시가 아흐레째인데 아직 안 보냈다 — 목록에는 있지만 눈에 안 걸린다. */
    chk('오래 밀린 재시를 짚는다',
        n0.rows.some(r => r[0] === '아직 안 보냄' && r[1] === '최나래'), true);
    chk('며칠째인지 말해 준다', n0.why.some(t => /9일째/.test(t)), true);

    /* '무시' 는 미루기를 그대로 쓴다 — 새로 저장할 곳을 만들지 않는다. */
    const off = await p.evaluate(async () => {
      const b = [].filter.call(document.querySelectorAll('#nudge .ndg'),
                               e => /최나래/.test(e.textContent))[0]
                  .querySelector('[data-ndgoff]');
      b.click();
      await new Promise(r => setTimeout(r, 300));
      return [].map.call(document.querySelectorAll('#nudge .who'), e => e.textContent);
    });
    chk('무시하면 내려간다', off.indexOf('최나래') < 0, true);
    /* 넛지를 무시했다고 재시 목록의 그 사람까지 미뤄지면 안 된다 —
       열쇠가 겹치면 그렇게 된다. */
    chk('재시 목록은 그대로 있다', await p.evaluate(() =>
      [].filter.call(document.querySelectorAll('#pendList .row'), e => e.offsetParent)
        .some(e => /최나래/.test(e.textContent))), true);
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
    chk('재시 문자를 DT 에서 빌려 온다', one, '빌린재시:최나래/ch1/12/재시/1');
    const two = await grab('#passList .mini.msg');
    chk('통과 문자도 빌려 온다', two, '빌린통과:김마루/ch2/7/정시/1/96');

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
     명단 셋(김마루·새학생·이아람), 갈라진 이름표 하나, DT 흉내 응답. */
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
    chk('한 줄에 두 앱이 모인다', roster[0], '김마루/휘문중/exam+km');

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
    /* ⚠ 이 둘은 카드 줄을 **통째로** 견줬다. 그래서 맨 위에 '아직 못 잡은
       개념' 한 줄이 늘자 뜻은 그대로인데 둘 다 빨간불이 됐다. 개념 줄은
       앱 기록이 아니라 **요약**이니 따로 세고, 나머지의 차례를 본다. */
    const 요약 = t => /아직 못 잡은 개념/.test(t);
    const 앱기록 = other.titles.filter(t => !요약(t));
    const 앱갈래 = other.kinds.filter((k, i) => !요약(other.titles[i]));
    chk('요약이 맨 위에 선다', 요약(other.titles[0]), true);
    chk('세 앱 기록이 한 카드에 선다', 앱기록,
        ['DT 시험 미응시', 'DT 통과 · 96점', '화학 정밀 학습진단']);
    chk('급한 것이 위에 선다', 앱갈래.map(k => k.replace(' sent','')), ['miss', 'pass', 'km']);
    /* 앞 화면(대시보드)에서 이 학생의 통과 문자를 이미 복사했다. 그 표시가
       학생 카드까지 따라와야 "보냈나?" 를 다시 세지 않는다. */
    chk('보낸 표시가 화면을 넘어 따라온다', other.kinds.filter(k => / sent/.test(k)), ['pass sent']);
    // 주소를 셸이 지어내면 저쪽이 경로를 바꾸는 날 조용히 어긋난다
    chk('설문 앱이 준 주소를 그대로 쓴다', other.kmUrl,
        'https://chemistreal.github.io/KMChC/report.html?id=k1');

    /* 이 한 줄이 syncWorkRows 의 존재 이유다. 대시보드와 카드가 서로 다르게
       잘라 담으면 여기서 **엉뚱한 학생 문구**가 나오고, 그대로 학부모에게 간다. */
    const msg = await clip('#stuOther .mini.msg[data-pass]');
    chk('카드에서 누른 문자가 그 학생 것이다', msg, '빌린통과:김마루/ch2/7/정시/1/96');
    const abs = await clip('#stuOther .mini.msg[data-abs][data-stage="1"]');
    chk('미응시 안내도 카드에서 바로', abs, '빌린미응시:김마루/ch1/12/빌린주소/ch1/12/1');
  }

  console.log('\n── 상담지 한 장 ──');
  {
    /* 학부모 상담은 매주 돌아온다. 자료는 이미 셸이 다 들고 있는데 종이로
       나가는 길만 없어서, 그때마다 세 앱을 오가며 손으로 옮겨 적었다. */
    const pr = await p.evaluate(async () => {
      let printed = 0;
      window.print = () => { printed++; };        // 인쇄창을 실제로 띄우지는 않는다
      const r = ROSTER.filter(x => x.name === '김마루')[0];
      openStudent(r);
      await new Promise(t => setTimeout(t, 700));
      document.getElementById('dlgPrint').click();
      await new Promise(t => setTimeout(t, 200));
      const el = document.getElementById('print');
      return {
        printed: printed,
        h1: (el.querySelector('h1') || {}).textContent,
        keys: [].map.call(el.querySelectorAll('.pr__k div span'), e => e.textContent),
        nums: [].map.call(el.querySelectorAll('.pr__k div b'), e => e.textContent),
        heads: [].map.call(el.querySelectorAll('h2'), e => e.textContent),
        memo: !!el.querySelector('.memo'),
        foot: (el.querySelector('.foot') || {}).textContent,
        onScreen: getComputedStyle(el).display,
        frames: el.querySelectorAll('iframe').length,
      };
    });
    console.log('  ' + JSON.stringify(pr.heads) + ' ' + JSON.stringify(pr.nums));
    chk('인쇄를 부른다', pr.printed, 1);
    chk('누구 것인지 적는다', pr.h1, '김마루 학습 상담지');
    chk('셀 것을 다 센다', pr.keys,
        ['파이널 응시', '평균 정답률', '가장 최근', 'DT 통과', '재시 대기', '미응시']);
    /* 화면 카드가 말하는 것과 종이가 말하는 것이 달라지면 어느 쪽이 맞는지
       물어야 한다 — 같은 함수를 쓴다(DT 통과 1 · 미응시 1). */
    chk('화면과 같은 숫자', [pr.nums[3], pr.nums[5]], ['1', '1']);
    /* 상담은 말로 한다. 적을 자리가 없으면 종이 뒤에 적게 된다. */
    chk('적을 자리가 있다', pr.memo, true);
    chk('무엇을 바탕으로 했는지 적는다', /DT 시트 기준/.test(pr.foot || ''), true);
    /* 화면에는 안 보여야 한다 — 보이면 대시보드 밑에 종이가 한 장 깔린다. */
    chk('화면에는 안 나온다', pr.onScreen, 'none');
    /* iframe 이 딸려 들어가면 종이가 여러 장이 되고 앱 화면이 통째로 찍힌다. */
    chk('앱 화면은 안 딸려 간다', pr.frames, 0);
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); });
    await p.waitForTimeout(200);
  }

  console.log('\n── 오늘 할 일을 한 줄에 세운다 ──');
  {
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(600);
    /* [바뀐 것] 2026-08-14 까지는 이 줄이 **두 벌**이었다 — 「오늘 할 일」(#todo)
       바로 아래 같은 칩 줄(#jump)이 글자까지 똑같이 서 있었다. 겹친 쪽을
       지웠다. 지키려던 것은 «오늘 할 일이 한 줄로 선다» 이지 «그 자리 이름이
       jump 다» 가 아니므로, 남은 자리를 본다. */
    const jump = await p.evaluate(() => ({
      shown: !document.getElementById('todo').hidden,
      labels: [].map.call(document.querySelectorAll('#todo .chip'),
        e => e.textContent.replace(/\s+/g, '')),
      dupRow: !!document.getElementById('jump'),
    }));
    console.log('  ' + JSON.stringify(jump.labels));
    chk('칩이 뜬다', jump.shown, true);
    chk('같은 줄이 두 번 안 선다', jump.dupRow, false);
    // 반이 아니라 사람 수로 세야 "몇 명에게 보내야 하나" 가 된다
    chk('미응시는 사람 수로 센다', jump.labels[0], '시험미응시2');
    chk('다섯 자리가 다 선다', jump.labels.length, 5);
    const jumped = await p.evaluate(() => {
      document.querySelector('#todo .chip[data-jump="passWrap"]').click();
      return document.getElementById('passWrap').classList.contains('flashed');
    });
    chk('누르면 그 자리를 짚어 준다', jumped, true);
  }

  console.log('\n── 늘 묻는 것은 칩 하나로 (저장된 보기) ──');
  {
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close();
                             try { localStorage.removeItem('chemistreal:views'); } catch (e) {}
                             history.replaceState(null, '', location.pathname);
                             show('dash'); renderViews(); });
    await p.waitForTimeout(300);
    /* ⚠ 여기는 한동안 문장을 통째로 붙들고 있었다. 그래서 문구를 사람이
       알아듣는 말로 고친 순간(2026-08-09) 이 자가 울렸다 — 나빠진 것이
       없는데 울린 것이다. 자가 지켜야 할 것은 **철자가 아니라 약속**이다:
       비어 있을 때는 (가) 걸어 두면 무엇이 좋아지는지 말하고,
       (나) 설명하는 대신 **실제로 하는 일 하나를 예로 든다.**
       예가 없으면 "걸어 두세요" 가 무엇을 걸라는 말인지 알 수 없다. */
    const empty = await p.evaluate(() => {
      const el = document.getElementById('views');
      return { lab: (el.querySelector('.vlab') || {}).textContent || '',
               note: (el.querySelector('.dim') || {}).textContent || '',
               eg: !!el.querySelector('.dim b') };
    });
    console.log('  ' + JSON.stringify(empty));
    chk('처음에는 비어 있다고 말해 준다', /저장|걸어 두|한 번에/.test(empty.note), true);
    chk('말 대신 실제로 하는 일을 예로 든다', empty.eg && /예:/.test(empty.note), true);
    /* 이름은 시스템 말이 아니라 사람이 알아보는 말이어야 한다 —
       '저장된 보기' 로 불렀을 때 선생님이 무엇인지 모르셨다. */
    chk('이름에 화면이라는 말이 들어간다', /화면/.test(empty.lab), true);

    /* 반 하나를 골라 둔 상태를 그대로 저장한다. 주소가 곧 상태라 담을 것이
       주소 한 줄뿐이다. */
    const saved = await p.evaluate(() => {
      CLS_PICK = '화학1 토1:30-5:30'; show('cls'); renderClassTab(); writeHash();
      document.getElementById('viewAdd').click();
      return { hash: location.hash,
               chips: [].map.call(document.querySelectorAll('#views .v > button:first-child'),
                                  e => e.textContent) };
    });
    console.log('  ' + JSON.stringify(saved.chips));
    chk('이름을 안 묻고 지금 화면에서 짓는다', saved.chips, ['반 · 화학1 토1:30-5:30']);
    /* 이미 저장한 화면에서는 저장 단추가 사라져야 한다 — 두 번 담으면 어느
       것이 최신인지 모른다. */
    chk('저장한 화면에서는 단추가 내려간다', await p.evaluate(() =>
      !document.getElementById('viewAdd')), true);

    /* 다른 데를 갔다가 칩 하나로 돌아온다 — 그게 이 기능의 전부다. */
    const backTo = await p.evaluate(async () => {
      show('dash'); await new Promise(r => setTimeout(r, 200));
      const had = document.querySelector('.pane.on').id;
      document.querySelector('#views .v > button[data-view]').click();
      await new Promise(r => setTimeout(r, 300));
      return { from: had, tab: document.querySelector('.pane.on').id,
               pick: CLS_PICK, hash: location.hash };
    });
    chk('다른 데로 갔다가', backTo.from, 'p-dash');
    chk('칩 하나로 그 자리로', backTo.tab, 'p-cls');
    chk('고른 것까지 그대로', backTo.pick, '화학1 토1:30-5:30');

    /* 브라우저를 닫았다 열어도 남아야 뜻이 있다. */
    await p.reload();
    await p.waitForTimeout(1200);
    chk('새로고침해도 남는다', await p.evaluate(() =>
      [].map.call(document.querySelectorAll('#views .v > button:first-child'), e => e.textContent)),
      ['반 · 화학1 토1:30-5:30']);

    /* 앱 화면(iframe)은 저장해도 뜻이 없다 — 그 안의 상태는 주소에 안 담긴다. */
    chk('앱 탭에서는 저장 단추가 없다', await p.evaluate(async () => {
      show('dtr'); await new Promise(r => setTimeout(r, 300));
      return !document.getElementById('viewAdd');
    }), true);

    const gone = await p.evaluate(async () => {
      show('dash'); await new Promise(r => setTimeout(r, 200));
      document.querySelector('#views .v .x').click();
      await new Promise(r => setTimeout(r, 200));
      return { n: document.querySelectorAll('#views .v').length,
               stored: localStorage.getItem('chemistreal:views') };
    });
    chk('지우면 없어진다', gone.n, 0);
    chk('저장된 것에서도 없어진다', gone.stored, '[]');
  }

  console.log('\n── 휴대폰에서도 탭이 다 보인다 ──');
  {
    /* 390px 에서 재어 보니 열두 탭 중 여섯만 보였다. 밀 수는 있는데 막대를
       숨겨 놔서 더 있다는 표시가 없었다 — 있는 줄도 모르고 지나간다. */
    const before = await p.viewportSize();
    await p.setViewportSize({ width: 390, height: 844 });
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(400);

    const m0 = await p.evaluate(() => {
      const navs = [].slice.call(document.querySelectorAll('header nav'));
      return { cut: navs.map(n => n.scrollWidth > n.clientWidth + 2),
               cls: navs.map(n => n.className),
               headH: Math.round(document.querySelector('header').getBoundingClientRect().height) };
    });
    chk('탭 줄이 잘린다', m0.cut, [true, true]);
    chk('잘린 쪽을 흐린다', m0.cls.every(c => /scr-r/.test(c)), true);
    /* 머리가 163px 이면 세로의 5분의 1을 숫자 하나 보기 전에 쓴다. */
    console.log('  머리 높이 ' + m0.headH + 'px');
    chk('머리가 화면을 덜 먹는다', m0.headH <= 130, true);

    /* Cmd+K 로 '수입' 에 가면 화면은 바뀌는데 밑줄 그어진 탭이 화면 밖이라
       아무 일도 안 일어난 것처럼 보인다. */
    const wasOff = await p.evaluate(() => {
      const b = document.getElementById('t-inc');
      return b.getBoundingClientRect().right > document.documentElement.clientWidth + 1;
    });
    chk('그 탭은 원래 화면 밖이었다', wasOff, true);
    await p.evaluate(() => show('inc'));
    await p.waitForTimeout(250);
    const far = await p.evaluate(() => {
      const b = document.getElementById('t-inc'), w = document.documentElement.clientWidth;
      const now = b.getBoundingClientRect();
      return { nowIn: now.left >= -1 && now.right <= w + 1,
               scrolled: window.scrollY + document.querySelector('main').scrollTop };
    });
    chk('고르면 보이는 자리로 온다', far.nowIn, true);
    /* 페이지까지 같이 밀면 보고 있던 자리를 잃는다. */
    chk('페이지는 안 밀린다', far.scrolled, 0);

    const back = await p.evaluate(() => {
      show('dash');
      const n = document.querySelector('header nav');
      return { left: n.scrollLeft, cls: n.className };
    });
    chk('첫 탭이면 처음으로 붙는다', back.left, 0);
    chk('처음이면 왼쪽은 안 흐린다', /scr-l/.test(back.cls), false);

    await p.setViewportSize(before);
    await p.waitForTimeout(300);
  }

  console.log('\n── 개념 하나로 아이들을 부른다 ──');
  {
    /* 대시보드의 '어려워하는 개념' 은 익명본이라 숫자까지만 말해 준다. 그걸
       보고 나서 할 수 있는 일이 없었다 — 누구인지를 모르니까. */
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); show('dash'); });
    await p.waitForTimeout(400);
    const jumped = await p.evaluate(() => {
      const b = document.querySelector('#misList .mini[data-mistag]');
      if (!b) return null;
      const tag = b.dataset.mistag;
      b.click();
      return { tag: tag, tab: document.querySelector('.pane.on').id, hash: location.hash };
    });
    chk('대시보드에서 누가 를 누르면 개념 탭으로', jumped && jumped.tab, 'p-con');
    chk('주소가 곧 상태', /^#con\?tag=/.test((jumped || {}).hash || ''), true);
    await p.waitForTimeout(900);

    const con = await p.evaluate(() => ({
      chips: [].map.call(document.querySelectorAll('#conTabs .chip'), e => e.textContent),
      head:  (document.getElementById('conHead') || { textContent: '' }).textContent.replace(/\s+/g, ' ').trim(),
      names: [].map.call(document.querySelectorAll('#conList .row .nm'), e => e.textContent),
      metas: [].map.call(document.querySelectorAll('#conList .row .where'), e => e.textContent),
      tags:  [].map.call(document.querySelectorAll('#conList .row .tag'), e => e.textContent),
    }));
    console.log('  ' + JSON.stringify(con.chips) + ' · ' + JSON.stringify(con.names));
    /* 몰농도는 세 줄인데 김마루이 두 줄이라 **2명**이다. 사람으로 안 묶으면
       3명으로 세고, 보충 자리를 하나 더 잡게 된다. */
    chk('많이 걸린 개념이 앞에 선다', con.chips[0], '몰농도2');
    chk('한 사람은 한 줄', con.names, ['김마루', '최나래']);
    /* 세 회차 내리 걸린 아이가 이번 주에 한 번 걸린 아이 아래로 내려가면,
       보충 자리는 위에서부터 차는 탓에 정작 필요한 쪽이 빠진다. */
    chk('되풀이해 걸린 아이가 위에 선다', con.names[0], '김마루');
    chk('몇 명인지 적는다', /몰농도.*2명|아직 못 잡은 학생 2명/.test(con.head), true);
    /* 통과했는데 여기 있으면 "얘는 통과했는데 왜" 가 되고, 목록 전체를 못 믿게 된다. */
    chk('통과했지만 이 개념은 틀림을 적는다',
        con.tags.filter(t => /통과/.test(t)), ['통과 · 이 개념은 틀림']);
    /* 오래된 회차를 보여 주면 "이거 벌써 했는데" 가 된다 — 최근 것으로 선다. */
    chk('같은 사람은 최근 회차로', /화학Ⅱ · 12회/.test(con.metas.join(' | ')), true);

    const other = await p.evaluate(() => {
      const c = [].filter.call(document.querySelectorAll('#conTabs .chip'),
                               e => /^완충/.test(e.textContent))[0];
      if (!c) return null;
      c.click();
      return { names: [].map.call(document.querySelectorAll('#conList .row .nm'), e => e.textContent),
               hash: location.hash };
    });
    /* 완충은 둘 다 한 회차씩이라 되풀이로 갈리지 않는다 — 최근 순이다
       (김도윤 2일 · 김마루 5일). 여기서 보는 것은 **누가 서는가**다. */
    chk('개념을 바꾸면 그 사람들이 선다', (other || {}).names, ['김도윤', '김마루']);
    chk('바꾼 것도 주소에 남는다', /tag=%EC%99%84%EC%B6%A9/.test((other || {}).hash || ''), true);

    /* ── 상담에서 먼저 나오는 물음이 카드 안에 있는가 ─────────────────
       "무엇이 부족한가" 는 상담에서 가장 많이 나오는 물음인데, 카드에는
       회차와 점수뿐이었다. 개념은 **개념 탭**에 개념별로 있어서, 학부모 앞에서
       카드를 닫고 열몇 개를 하나씩 눌러 이 아이가 들었는지 봐야 했다.
       자료는 이미 와 있었다(mistags) — 학생 쪽으로 뒤집어 놓지 않았을 뿐이다. */
    /* ⚠ 고정 대기도, 화면 안에서 도는 폴링도 쓰지 않는다. 폴링은 그 자체가
       또 하나의 짐작이고(`tools/blind_wait.py` 가 세어 준다), 브라우저 밖에서
       `waitForFunction` 을 쓰면 그마저 없앨 수 있다. */
    await p.evaluate(() => {
      const d = document.getElementById('dlg'); if (d.open) d.close();
      show('stu');
    });
    await p.waitForFunction(() => [].some.call(
      document.querySelectorAll('#stuList .row'), e => /김마루/.test(e.textContent)),
      null, { timeout: 10000 });
    await p.evaluate(() => {
      [].filter.call(document.querySelectorAll('#stuList .row'),
                     e => /김마루/.test(e.textContent))[0].click();
    });
    /* 카드가 열리고 **다른 앱 기록까지** 붙을 때까지 기다린다. 열린 것만 보고
       재면 아직 비어 있는 카드를 재게 된다. */
    await p.waitForFunction(() => document.getElementById('dlg').open &&
      document.querySelectorAll('#dlgBody .trk__i').length > 0, null, { timeout: 10000 });
    const stuCon = await p.evaluate(() => {
      const box = [].filter.call(document.querySelectorAll('#dlgBody .trk__i'),
                                 e => /아직 못 잡은 개념/.test(e.textContent))[0];
      return box ? box.innerText.replace(/\s+/g, ' ').trim() : '';
    });
    console.log('  카드 안: ' + stuCon);
    chk('카드에 못 잡은 개념이 선다', /아직 못 잡은 개념/.test(stuCon || ''), true);
    /* 되풀이한 것이 먼저다 — 보충 자리는 위에서부터 찬다. */
    chk('되풀이한 개념이 앞이다', /몰농도\s*2회/.test(stuCon || ''), true);
    /* 거기서 개념 탭으로 넘어가면 **같은 개념을 못 잡은 다른 아이들**이 같이
       보인다(보충 묶기). 카드는 닫아야 한다 — 덮고 있으면 넘어간 뜻이 없다. */
    await p.evaluate(() => {
      const b2 = document.querySelector('#dlgBody [data-constu]');
      if (b2) b2.click();
    });
    await p.waitForFunction(() => document.querySelector('.pane.on').id === 'p-con' &&
      !document.getElementById('dlg').open, null, { timeout: 10000 }).catch(() => {});
    const jump2 = await p.evaluate(() => ({
      탭: document.querySelector('.pane.on').id,
      카드: document.getElementById('dlg').open,
      고른개념: (document.querySelector('#conTabs .chip.on') || {}).textContent,
    }));
    chk('카드에서 개념 탭으로 넘어간다', (jump2 || {}).탭, 'p-con');
    chk('넘어가면 카드는 닫는다', (jump2 || {}).카드, false);
    chk('가장 많이 걸린 개념이 골라져 있다', /^몰농도/.test((jump2 || {}).고른개념 || ''), true);

    /* 한 번 틀린 아이와 두 회차 내리 걸린 아이는 다른 아이다. 김마루은
       ch2#7 · ch1#4 두 회차에서 몰농도에 걸렸다. */
    const back = await p.evaluate(() => {
      const c = [].filter.call(document.querySelectorAll('#conTabs .chip'),
                               e => /^몰농도/.test(e.textContent))[0];
      c.click();
      return {
        marks: [].map.call(document.querySelectorAll('#conList .row .tag'), e => e.textContent),
        head:  (document.getElementById('conHead') || { textContent: '' }).textContent.replace(/\s+/g, ' '),
        mats:  [].map.call(document.querySelectorAll('#conHead a'), e => e.getAttribute('href')),
      };
    });
    chk('되풀이를 줄에 적는다', back.marks.filter(m => /회차 걸림/.test(m)), ['2회차 걸림']);
    chk('머리에도 몇 명인지 적는다', /두 회차 이상 걸린 1명/.test(back.head), true);
    /* 명단만 뽑고 자료를 다시 찾아 헤매면 보충 준비가 두 번 일이 된다.
       주소는 지어내지 않는다 — 검사용 자료 목록에 있는 것만 걸려야 한다. */
    console.log('  ' + JSON.stringify(back.mats));
    chk('있는 자료를 건다', back.mats.sort(),
        ['../DT/haeseol_ch1_round01.html', '../DT/haeseol_ch2_round12.pdf',
         '../DT/munje_ch1_round01.html', '../DT/munje_ch2_round12.html']);
    /* 7회는 자료 목록에 없다. 회차 이름은 적되 **주소는 안 짓는다** —
       지어내면 눌러 보고 나서야 404 를 안다. */
    chk('없는 회차도 적기는 한다', /화학Ⅱ 7회/.test(back.head), true);
    chk('없는 회차 주소를 지어내지 않는다',
        back.mats.some(h => /round0?7/.test(h)), false);

    const only = await p.evaluate(async () => {
      const b = document.querySelector('#conHead .mini[data-conact="repeat"]');
      if (!b) return null;
      const label = b.textContent;
      b.click();
      await new Promise(r => setTimeout(r, 200));
      return { label: label,
               names: [].map.call(document.querySelectorAll('#conList .row .nm'), e => e.textContent) };
    });
    chk('되풀이만 보는 단추가 있다', (only || {}).label, '되풀이만 1명');
    chk('누르면 그 아이만 선다', (only || {}).names, ['김마루']);
    await p.evaluate(() => document.querySelector('#conHead .mini[data-conact="repeat"]').click());

    /* 보충을 앉히려면 이름 목록이 있어야 한다. */
    const copied = await p.evaluate(async () => {
      document.querySelector('#conHead .mini[data-conact="names"]').click();
      await new Promise(r => setTimeout(r, 300));
      return navigator.clipboard.readText();
    });
    chk('이름을 한 번에 복사한다', copied, '김마루, 최나래');
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
    chk('미응시 두 명이 서 있다', before, ['김도윤', '김마루']);

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
      /* 겹쳐 있던 칩 줄(#jump)은 지웠다 — 「오늘 할 일」(#todo)이 같은 배열로
         같은 글자를 이미 적고 있었다(2026-08-14). 재는 것은 그대로다:
         **미룬 것이 오늘 할 일에서 빠지는가.** */
      chip: (document.querySelector('#todo .chip[data-jump="absWrap"]')
             || { textContent: '' }).textContent.replace(/\s+/g, ''),
      /* 숫자 카드는 반 상태다. 미뤘다고 미응시가 한 명 줄어드는 것은 아니다 —
         줄이면 "학생이 시험을 봤다" 로 읽힌다. */
      card: (document.getElementById('abCnt') || { textContent: '' }).textContent,
    }));
    console.log('  ' + JSON.stringify(after.seen) + ' · ' + after.bar);
    chk('미룬 줄은 눈에서 내려간다', after.seen, ['김마루']);
    chk('지운 것이 아니라 접은 것이다', after.kept, 2);
    chk('몇을 미뤘는지 말해 준다', /미룬 것 1명/.test(after.bar), true);
    /* 오늘 할 일에서는 빠져야 한다 — 그게 미루기의 전부다. */
    chk('오늘 할 일에서 빠진다', after.chip, '시험미응시1');
    /* 반 상태에서까지 빼면 학생이 사라진 것처럼 보인다. 넣되 적는다
       (그림 쪽 '미룬 N명 포함' 은 명단이 있어야 그려지므로 tests/hub.js 가 본다). */
    chk('반 상태 숫자는 그대로다', after.card, '2');

    const shown = await p.evaluate(() => {
      document.querySelector('#absList .snzbar .mini[data-snzshow]').click();
      return [].filter.call(document.querySelectorAll('#absList .row.sub'), e => e.offsetParent)
               .map(e => e.querySelector('.nm').textContent);
    });
    chk('펼치면 다시 보인다', shown, ['김도윤', '김마루']);

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
      /* 겹쳐 있던 칩 줄(#jump)은 지웠다 — 「오늘 할 일」(#todo)이 같은 배열로
         같은 글자를 이미 적고 있었다(2026-08-14). 재는 것은 그대로다:
         **미룬 것이 오늘 할 일에서 빠지는가.** */
      chip: (document.querySelector('#todo .chip[data-jump="absWrap"]')
             || { textContent: '' }).textContent.replace(/\s+/g, ''),
      bar:  !!document.querySelector('#absList .snzbar'),
    }));
    chk('무르면 도로 올라온다', back.seen, ['김도윤', '김마루']);
    chk('오늘 할 일에도 도로 잡힌다', back.chip, '시험미응시2');
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
    /* ⚠ 예전에는 문장을 **글자 그대로** 견줬다. 그래서 빈 상태에 '다음에 할
       일'(위의 전체를 누르면 다 보입니다)을 덧붙이자 뜻은 그대로인데 검사만
       빨간불이 됐다. 자가 문구를 붙들면 문구를 못 고친다 — **가른다는 사실**만
       본다: 검색이 없다고 하지 말고 조건 때문이라고 해야 한다. */
    chk('비면 조건 때문이라고 말한다',
        /이 조건에 맞는 학생이 없습니다/.test(none) && !/찾는 학생이 없습니다/.test(none), true);
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
    chk('이름·학교가 들어간다', /김마루\t휘문중\t\d+\t\d+\t\d+/.test(lines[1]), true);

    /* 화면은 120명만 보여 준다. 복사까지 잘리면 공지에서 아이가 빠지는데,
       빠진 줄도 모른다. */
    const names = await clip('#dlgBody .mini[data-rnd="names"]');
    console.log('  ' + JSON.stringify(names));
    chk('안 본 학생 이름이 공지에 붙는 모양으로', names, '새학생, 이아람');
    /* ── 어느 오답으로 쏠렸나 ──────────────────────────────────────
       화학은 오답 선택지가 곧 오개념이다. 그 계산은 **파이널 앱이 이미 하고
       있다** — 없던 것은 계산이 아니라 회차에서 들어가는 길이었다.
       ⚠ 성적표를 여는 길이므로 **기록이 늘면 안 된다**(파이널은 `#r=` 를 받으면
       다시 채점한다). 이 검사가 그것도 센다. */
    const anaBefore = await p.evaluate(() =>
      JSON.parse(localStorage.getItem('final:roster:jmchc-2') || '[]').length);
    const ana = await p.evaluate(async () => {
      const b = document.querySelector('#dlgBody .mini[data-rnd="ana"]');
      if (!b) return null;
      b.click();
      await new Promise(r => setTimeout(r, 900));
      return { tab: document.querySelector('.pane.on').id,
               open: document.getElementById('dlg').open };
    });
    chk('회차에서 문항 분석으로 간다', (ana || {}).tab, 'p-exam');
    chk('회차 창은 닫힌다', (ana || {}).open, false);
    /* 지켜야 할 것은 **없던 학생이 생기지 않는 것**이다. 재어 보니 2 → 1 로
       줄었는데, 이건 앞 검사가 일부러 심어 둔 '김 마루'(띄어쓴 같은 학생)이
       성적표를 다시 여는 순간 파이널의 저장 규칙(공백을 지운다)에 따라 붙은
       것이다 — 갈라진 이름이 하나로 돌아온 것이지 잃은 것이 아니다.
       그래서 '늘지 않는다' 와 '그 학생이 그대로 있다' 둘로 나눠 본다. */
    const anaAfter = await p.evaluate(() =>
      JSON.parse(localStorage.getItem('final:roster:jmchc-2') || '[]').map(r => r.name));
    console.log('  ' + JSON.stringify(anaAfter));
    chk('없던 학생이 생기지 않는다', anaAfter.length <= anaBefore, true);
    chk('그 학생은 그대로 있다', anaAfter.some(n => n.replace(/\s+/g, '') === '김마루'), true);
    await p.evaluate(() => { const d = document.getElementById('dlg'); if (d.open) d.close(); });
    await p.evaluate(() => show('rnd'));
    await p.waitForTimeout(300);
    await p.evaluate(() => openRound('jmchc-2'));
    await p.waitForTimeout(400);
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
    /* ── 창구 응답이 다 왔는지로 기다린다 ────────────────────────────
       반 화면은 창구를 **네 번 나눠** 부른다(names·pending·passed·absentees).
       어느 하나가 아직 안 왔는데 화면이 잠깐 멎으면 다 그려진 것으로 잘못
       읽는다. 실제로 그렇게 깨졌다 — 범례가 "아직 4" 하나뿐이었다(미응시·
       통과가 안 와서 넷 다 '아직' 으로 보인 것이다).
       화면 모양으로 기다리면 이 틈을 못 막는다. 응답 자체를 센다. */
    const need3 = new Set(['names', 'pending', 'passed', 'absentees']);
    let allIn3;
    const served3 = new Promise(res => { allIn3 = res; });
    const waitServed3 = (ms) => Promise.race([
      served3,
      new Promise((_, rej) => setTimeout(() => rej(new Error(
        '안 온 창구: ' + [...need3].join(', '))), ms)),
    ]).catch(e => { console.log('  FAIL  ' + e.message); fail++; });
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
      need3.delete(act);
      if (!need3.size) allIn3();
      return route.fulfill({ status: 200, contentType: 'application/javascript',
                             body: cb + '(' + JSON.stringify(body) + ')' });
    });
    /* 열쇠칸은 오리진 하나에 하나뿐이라, 앞에서 넣어 둔 것이 이 창에도 남아
       있다. 잠금을 보려면 먼저 비운다(같은 오리진의 아무 화면에서나 지운다). */
    await p3.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'domcontentloaded' });
    await p3.evaluate(() => localStorage.removeItem('chemistreal:gate'));
    await p3.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await until(p3, '잠금 화면이 뜬다', () => !!document.getElementById('gateGo'));
    /* 이 창은 열쇠칸이 비어 있다 — 먼저 잠금이 뜨는지 본다. */
    chk('처음 들어오면 코드를 묻는다', await p3.evaluate(() => !!document.getElementById('gate')), true);
    chk('잠긴 동안에는 창구를 안 부른다',
        await p3.evaluate(() => document.querySelectorAll('#connBar .conn').length), 0);
    await p3.fill('#gateIn', '1234');
    await p3.click('#gateGo');
    chk('틀린 코드로는 안 열린다', await p3.evaluate(() => !!document.getElementById('gate')), true);
    await p3.fill('#gateIn', '0000');
    await p3.click('#gateGo');
    /* 잠금이 풀리면 그제야 창구를 부른다. 둘 다 멎을 때까지 기다린다 —
       '잠금이 없어졌는가' 로만 기다리면 창구 세는 다음 줄이 이르게 0 을 본다. */
    await settled(p3, '잠금이 풀리고 창구가 붙는다',
      () => [!!document.getElementById('gate'),
             document.querySelectorAll('#connBar .conn').length], null, 30000);
    chk('맞히면 열린다', await p3.evaluate(() => !!document.getElementById('gate')), false);
    chk('열리면 그제야 부른다',
        await p3.evaluate(() => document.querySelectorAll('#connBar .conn').length > 0), true);

    await p3.evaluate(() => show('cls'));
    /* 반 화면은 창구를 **여러 번 나눠** 부른다(명단·미응시·통과·재시가 저마다
       온다). 그래서 '멎었나' 만으로는 이르다 — 부하가 걸리면 응답 사이가
       벌어져 그 틈을 다 그려진 것으로 잘못 읽는다. 실제로 CPU 를 여섯 배로
       물리면 여덟 번 중 여섯 번이 여기서 깨졌다.
       올 것이 다 왔는지 먼저 보고, 그다음에 멎기를 기다린다. */
    await waitServed3(30000);          // 네 창구가 다 대답할 때까지
    await until(p3, '반 화면이 그려진다', () =>
      document.querySelectorAll('#clsTabs .chip').length >= 2 &&
      document.querySelectorAll('#clsList .row').length >= 4 &&
      [].every.call(document.querySelectorAll('#clsList .row'),
                    r => r.querySelector('.nm') && r.querySelector('.tag')) &&
      document.querySelectorAll('#clsHead .legend button.lg').length > 0 &&
      document.querySelectorAll('#clsHead .stack i').length > 0 &&
      !!document.querySelector('#clsHead .donut span'), null, 30000);
    await settled(p3, '반 화면이 멎는다', () => [
      [].map.call(document.querySelectorAll('#clsTabs .chip'), e => e.textContent),
      [].map.call(document.querySelectorAll('#clsList .row'),
                  r => r.querySelector('.nm').textContent + '/' + r.querySelector('.tag').textContent),
      document.querySelectorAll('#clsHead .stack i').length,
    ], null, 30000);
    const cls = await p3.evaluate(() => ({
      tabs: [].map.call(document.querySelectorAll('#clsTabs .chip'), e => e.textContent),
      rows: [].map.call(document.querySelectorAll('#clsList .row'), r => [
        r.querySelector('.nm').textContent, r.querySelector('.tag').textContent]),
      /* 범례는 이제 누를 수 있는 단추다(막대 조각은 손가락으로 짚기엔 너무 얇다). */
      legend: [].map.call(document.querySelectorAll('#clsHead .legend button.lg'), e => e.textContent),
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
    /* ── 막대에서 목록으로 파고든다 ────────────────────────────────
       여태 막대는 보기만 하는 것이었다. "미응시 2명" 을 보고 그 둘이 누구인지
       알려면 목록을 눈으로 훑어야 했다. */
    const drill = await p3.evaluate(async () => {
      const before = [].map.call(document.querySelectorAll('#clsList .row .nm'), e => e.textContent);
      const b = document.querySelector('#clsHead .legend button.lg[data-segv="miss"]');
      if (!b) return null;
      b.click();
      await new Promise(r => setTimeout(r, 250));
      return { before: before,
               after: [].map.call(document.querySelectorAll('#clsList .row .nm'), e => e.textContent),
               note: (document.querySelector('#clsHead .note2') || { textContent:'' }).textContent.replace(/\s+/g,' ').trim(),
               hash: location.hash,
               pressed: document.querySelector('#clsHead .legend button.lg[data-segv="miss"]').getAttribute('aria-pressed') };
    });
    chk('누르기 전에는 반 전체', (drill || {}).before, ['가', '나', '다', '라']);
    chk('누르면 그 사람들만 남는다', (drill || {}).after, ['가', '나']);
    /* 걸러 놓은 것을 안 적으면 "왜 애가 둘밖에 없지" 가 된다. */
    chk('걸러 놓은 것을 적는다', /미응시만 보는 중 · 2명/.test((drill || {}).note || ''), true);
    chk('푸는 길을 그 자리에 둔다', /전체 보기/.test((drill || {}).note || ''), true);
    chk('눌린 티가 난다', (drill || {}).pressed, 'true');
    /* 주소가 곧 상태라, 걸러 놓은 채로 저장·공유가 된다. */
    chk('주소에 남는다', /[?&]s=miss/.test((drill || {}).hash || ''), true);

    /* 같은 것을 다시 누르면 풀린다 — 끄는 길을 따로 찾게 하지 않는다. */
    const off = await p3.evaluate(async () => {
      document.querySelector('#clsHead .legend button.lg[data-segv="miss"]').click();
      await new Promise(r => setTimeout(r, 250));
      return { n: document.querySelectorAll('#clsList .row').length,
               note: !!document.querySelector('#clsHead .note2'), hash: location.hash };
    });
    chk('다시 누르면 풀린다', off.n, 4);
    chk('풀리면 알림도 내려간다', off.note, false);
    chk('주소에서도 빠진다', /[?&]s=/.test(off.hash), false);

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

  /* ── 키보드로 훑을 때 어디에 서 있는지 보인다 ──────────────
     `.row:focus-visible` 이 outline 을 지우고 옅은 옥색 배경만 남겼던 적이
     있다. 그 배경(--wash #EDF4F1)은 종이색과 **1.13:1** 이라 사실상 아무
     표시도 아니었다. 마우스로만 써 보면 절대 안 보이는 결함이라 여기서 잰다. */
  console.log('\n── 키보드로 훑어도 어디인지 보인다 ──');
  {
    const p4 = await ctx.newPage();
    await p4.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await until(p4, '셸이 다 뜬다(초점 검사)',
      () => typeof show === 'function' && typeof EXAMS !== 'undefined' && EXAMS.length);
    /* 줄은 학생 탭에 있다. 대시보드에서는 Tab 이 닿지 않는다. */
    await p4.evaluate(() => show('stu'));
    await settled(p4, '학생 목록이 다 그려진다', () =>
      [].filter.call(document.querySelectorAll('.row'), r => r.getBoundingClientRect().width > 0).length);
    /* 줄이 아예 없으면 이 검사는 아무것도 안 본 채 통과할 수 있다. 먼저 센다. */
    const rowN = await p4.evaluate(() =>
      [].filter.call(document.querySelectorAll('.row'), r => r.getBoundingClientRect().width > 0).length);
    chk('훑을 줄이 있다', rowN > 0, true);
    /* ⚠ 스크립트로 focus() 만 부르면 :focus-visible 이 안 걸린다 — 크로뮴은
       **마지막 조작이 키보드였나**를 본다. 실제로 Tab 을 눌러야 한다. */
    let ring = { 못찾음: true };
    for (let i = 0; i < 60; i++) {
      await p4.keyboard.press('Tab');
      const r = await p4.evaluate(() => {
        const a = document.activeElement;
        if (!a || !a.classList || !a.classList.contains('row')) return null;
        const cs = getComputedStyle(a);
        return { 두께: parseFloat(cs.outlineWidth) || 0, 모양: cs.outlineStyle };
      });
      if (r) { ring = r; break; }
    }
    console.log('  테두리 ' + JSON.stringify(ring));
    chk('줄에 초점이 오면 테두리가 보인다',
        !ring.못찾음 && ring.모양 !== 'none' && ring.두께 >= 2, true);
    await p4.close();
  }

  /* 한글 자판에서 자음만 치면 낱자가 남는다. 순수 함수는 tests/hub.js 가 재고,
     여기서는 **화면이 실제로 줄어드는지**를 본다 — 함수가 맞아도 찾기 칸이
     그 함수를 안 쓰면 아무것도 안 달라진다(예전에 세 칸 중 한 곳만 고쳤다). */
  console.log('\n── 초성으로 찾으면 목록이 줄어든다 ──');
  {
    const p5 = await ctx.newPage();
    await p5.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await until(p5, '셸이 다 뜬다(초성 검사)',
      () => typeof show === 'function' && typeof EXAMS !== 'undefined' && EXAMS.length);
    await p5.evaluate(() => show('stu'));
    await settled(p5, '명단이 다 그려진다',
      () => document.querySelectorAll('#stuList .row .nm').length);
    const named = async () => p5.evaluate(() =>
      [].map.call(document.querySelectorAll('#stuList .row .nm'), e => e.textContent));
    console.log('  명단 ' + JSON.stringify(await named()));
    chk('명단에 이름이 있다', (await named()).length > 1, true);
    /* '이아람' 의 초성. 한글 IME 없이도 낱자는 그대로 넣을 수 있다.
       ⚠ 앞선 검사들이 명단을 바꿔 놓는다 — 여기 있는 이름으로 골라야 한다. */
    await p5.evaluate(() => {
      const q = document.getElementById('q');
      q.value = 'ㅇㅇㄹ'; q.dispatchEvent(new Event('input'));
    });
    await p5.waitForTimeout(200);
    chk('초성만 쳐도 그 학생이 남는다', await named(), ['이아람']);
    /* 조합 중인 글자('김ㅁ')에서 목록이 비지 않아야 한다 — 치는 도중의 한 순간이다. */
    await p5.evaluate(() => {
      const q = document.getElementById('q');
      q.value = '김ㅁ'; q.dispatchEvent(new Event('input'));
    });
    await p5.waitForTimeout(200);
    chk('치는 도중에도 안 비워진다', (await named()).indexOf('김마루') >= 0, true);

    /* 상담 주간에는 한 반을 차례로 훑는다. 카드를 닫고 다음 이름을 찾아 다시
       여는 일이 스무 번 되풀이됐다. 목록에서 연 카드는 ← → 로 넘어가야 한다. */
    console.log('\n── 학생 카드에서 옆 사람으로 ──');
    await p5.evaluate(() => {
      const q = document.getElementById('q');
      q.value = ''; q.dispatchEvent(new Event('input'));
    });
    await p5.waitForTimeout(200);
    const list = await named();
    await p5.click('#stuList .row');
    await p5.waitForTimeout(400);
    const shown = () => p5.evaluate(() => ({
      이름: document.getElementById('dlgName').textContent,
      자리: document.getElementById('dlgAt').textContent,
      단추: !document.getElementById('dlgNav').hidden,
      앞: document.getElementById('dlgPrev').disabled,
    }));
    let st = await shown();
    chk('첫 학생이 열린다', st.이름, list[0]);
    chk('넘김 단추가 보인다', st.단추, true);
    chk('몇 번째인지 적는다', st.자리, '1 / ' + list.length);
    chk('맨 앞에서는 앞으로 못 간다', st.앞, true);
    await p5.keyboard.press('ArrowRight');
    await p5.waitForTimeout(400);
    st = await shown();
    chk('→ 로 다음 사람', [st.이름, st.자리], [list[1], '2 / ' + list.length]);
    await p5.keyboard.press('ArrowLeft');
    await p5.waitForTimeout(400);
    chk('← 로 되돌아온다', (await shown()).이름, list[0]);
    /* 목록 없이 연 카드에는 넘길 곳이 없다 — 단추가 남으면 안 된다. */
    await p5.evaluate(() => { document.getElementById('dlg').close(); });
    await p5.waitForTimeout(200);
    await p5.evaluate(() => openStudent({ name:'혼자', school:'', grade:'', apps:{} }));
    await p5.waitForTimeout(400);
    chk('혼자 열면 단추가 안 보인다', (await shown()).단추, false);
    await p5.close();
  }

  /* 수업이 끝나면 반마다 "오늘 뭘 배웠다" 를 보낸다. 열두 명이면 열두 번,
     이름만 바꿔 손으로 붙여 넣었다. 여기서는 **실제로 열두 통이 나오는지**를 본다. */
  console.log('\n── 수업 문자: 반 하나로 사람 수만큼 ──');
  {
    const p6 = await ctx.newPage();
    /* 창구 대답은 창마다 따로 꾸민다(route 는 창에 붙는다). 반 넷짜리 한 반이면
       "사람 수만큼 나오는가" 를 세기에 넉넉하다. */
    await p6.route('**/macros/s/**', route => {
      const u = new URL(route.request().url());
      const cb = u.searchParams.get('callback'), act = u.searchParams.get('action');
      const isDT = u.pathname.includes(DT_EP);
      const body = (isDT && act === 'names') ? { ok: true, classes: [
            { label:'화학1 토1:30', course:'ch1', students:[
              {name:'가',school:'A중',year:'2'},{name:'나',school:'A중',year:'2'},
              {name:'다',school:'A중',year:'2'},{name:'라',school:'A중',year:'2'}] }] }
        : act === 'names' ? { ok: true, students: [] }
        : act === 'pending' ? { ok: true, pending: { stale: [], active: [] } }
        : act === 'passed' ? { ok: true, passed: { passed: [] } }
        : act === 'absentees' ? { ok: true, absentees: { classes: [] } }
        : { ok: true, rows: [] };
      return route.fulfill({ status: 200, contentType: 'application/javascript',
                             body: cb + '(' + JSON.stringify(body) + ')' });
    });
    /* 회차 칸은 DT 자료 목록에서 온다. 화학Ⅰ 세 회차짜리로 꾸민다. */
    await p6.route('**/DT/materials.json', route => route.fulfill({
      status: 200, contentType: 'application/json; charset=utf-8',
      body: JSON.stringify({ courses: [
        { key: 'ch1', name: '화학Ⅰ', rounds: [{ round: 1 }, { round: 2 }, { round: 3 }] }] }),
    }));
    await p6.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await until(p6, '셸이 다 뜬다(회차 글 검사)',
      () => typeof show === 'function' && typeof EXAMS !== 'undefined' && EXAMS.length);
    /* 앞 검사가 남긴 회차 글이 있으면 셈이 어긋난다 — 빈 상태에서 시작한다. */
    await p6.evaluate(() => localStorage.removeItem('chemistreal:lessons'));
    await p6.evaluate(() => show('cls'));
    await p6.waitForSelector('.mini[data-clsact="lesson"]', { timeout: 20000 });
    await p6.click('.mini[data-clsact="lesson"]');
    await p6.waitForTimeout(300);
    chk('반에서 창이 열린다', await p6.evaluate(() => document.getElementById('les').open), true);
    /* '＋ 새 회차' 를 열여덟 번 누르게 하면 안 된다 — DT 회차만큼 칸이 서 있어야 한다. */
    await p6.waitForFunction(() => {
      const sel = document.getElementById('lesPick');
      return sel && sel.options.length >= 3;
    }, { timeout: 15000 });
    const slots = await p6.evaluate(() => ({
      칸: document.getElementById('lesPick').options.length,
      첫칸: document.getElementById('lesPick').options[0].textContent,
      센것: document.getElementById('lesBody').textContent.match(/\d+\/\d+ 적음/)?.[0],
    }));
    chk('DT 회차만큼 칸이 선다', slots.칸, 3);
    chk('빈 칸이라고 알려 준다', /아직 안 적음/.test(slots.첫칸), true);
    chk('몇 칸 적었는지 적는다', slots.센것, '0/3 적음');
    /* 빈 칸을 고르면 빈 미리보기 대신 무엇을 하면 되는지 말해야 한다. */
    chk('빈 칸에는 할 일을 적는다',
        await p6.evaluate(() => /고치기.*눌러/.test(document.getElementById('lesBody').textContent)), true);

    await p6.click('.mini[data-les="edit"]');
    await p6.waitForTimeout(250);
    chk('고치기가 열린다',
        await p6.evaluate(() => !!document.getElementById('lesBodyIn')), true);
    /* ── 이름을 손으로 안 넣어도 된다 ────────────────────────────────
       본문에 {이름} 이 없어도 머리말로 이름이 저절로 붙어야 한다. 이것이
       "이름까지 자동" 의 자리다. */
    await p6.evaluate(() => {
      const ta = document.getElementById('lesBodyIn');
      ta.value = '안녕하세요. 화학올림피아드 담당하는 조준모입니다.';
      document.getElementById('lesTitle').value = '자동 이름';
    });
    await p6.click('.mini[data-les="save"]');
    await p6.waitForTimeout(300);
    const autoP = await p6.evaluate(() => ({
      미리보기: document.querySelector('.les__pre').textContent,
      안내: /머리말로 이름이 자동으로/.test(document.getElementById('lesBody').textContent),
      한통: (function(){ const c = lesCur(), w = lesWho()[0]; return lesText(c, w, LES_CLS); })(),
    }));
    chk('이름을 안 넣어도 머리말이 붙는다', /^가 학생 학부모님께/.test(autoP.미리보기.trim()), true);
    chk('자동으로 붙는다고 알려 준다', autoP.안내, true);
    chk('복사되는 한 통에도 들어간다', /^가 학생 학부모님께\n\n안녕하세요/.test(autoP.한통), true);
    /* 학생마다 달라야 한다 — 안 그러면 자동으로 붙여도 뜻이 없다. */
    const each = await p6.evaluate(() => lesWho().map(s => lesText(lesCur(), s, LES_CLS).split('\n')[0]));
    chk('통마다 이름이 다르다', new Set(each).size, each.length);

    await p6.click('.mini[data-les="edit"]');
    await p6.waitForTimeout(200);
    /* 자리표시자는 커서 자리에 들어가야 한다 — 끝에 붙으면 옮겨 적어야 한다. */
    await p6.evaluate(() => {
      const ta = document.getElementById('lesBodyIn');
      ta.value = '안녕하세요. 학생 학부모님.'; ta.selectionStart = ta.selectionEnd = 7;
    });
    await p6.click('[data-lesmark="{이름}"]');
    await p6.waitForTimeout(120);
    chk('자리표시자가 커서 자리에 들어간다',
        await p6.evaluate(() => document.getElementById('lesBodyIn').value),
        '안녕하세요. {이름}학생 학부모님.');

    await p6.evaluate(() => { document.getElementById('lesTitle').value = '화학의 기초'; });
    await p6.click('.mini[data-les="save"]');
    await p6.waitForTimeout(300);
    const view = await p6.evaluate(() => ({
      담김: JSON.parse(localStorage.getItem('chemistreal:lessons') || '{}').lessons.length,
      고르개: !!document.getElementById('lesPick'),
      미리보기: document.querySelector('.les__pre').textContent,
      사람수: document.querySelectorAll('[data-lesone]').length,
    }));
    chk('처음 적을 때 담긴다', view.담김, 1);
    chk('회차 고르개가 그대로', view.고르개, true);
    chk('미리보기가 첫 학생 이름으로 채워진다', /\{이름\}/.test(view.미리보기), false);
    chk('사람 수만큼 복사 단추', view.사람수 > 0, true);

    /* 열두 통이 한 덩어리로 나와야 한다 — 이름 사이에 머리를 넣는다. */
    const bulk = await p6.evaluate(() => {
      const cur = lesCur(), who = lesWho();
      return who.map(s => '── ' + s.name + ' ──\n' + lesFill(cur.body, s, LES_CLS, cur.round)).join('\n\n');
    });
    const heads = (bulk.match(/── .+ ──/g) || []).length;
    chk('사람 수만큼 통이 나온다', heads, view.사람수);
    chk('통마다 그 학생 이름이 들어간다', /\{이름\}/.test(bulk), false);

    /* 머리말도 비우고 본문에도 {이름} 이 없으면, 그때는 열두 통이 정말 같은
       글이 된다. 그 경우에만 붉게 짚는다(머리말이 있으면 자동으로 붙으니까). */
    await p6.click('.mini[data-les="edit"]');
    await p6.waitForTimeout(200);
    await p6.evaluate(() => { document.getElementById('lesBodyIn').value = '이름 없는 글'; });
    await p6.click('.mini[data-les="save"]');
    await p6.waitForTimeout(250);
    chk('머리말이 있으면 안 짚는다(자동으로 붙으니까)',
        await p6.evaluate(() => !!document.querySelector('#lesBody .note.err')), false);
    await p6.evaluate(() => { LES_HEAD = ''; lesSave(); lesRender(); });
    await p6.waitForTimeout(200);
    chk('머리말까지 비면 붉게 짚는다',
        await p6.evaluate(() => !!document.querySelector('#lesBody .note.err')), true);
    await p6.evaluate(() => { LES_HEAD = null; lesSave(); });

    /* 지우기는 고치는 중에만 있다 — 보기 화면에서 실수로 눌리면 안 된다. */
    await p6.click('.mini[data-les="edit"]');
    await p6.waitForTimeout(200);
    await p6.click('.mini[data-les="del"]');
    await p6.waitForTimeout(250);
    chk('지우면 담긴 것에서 빠진다(칸은 남는다)',
        await p6.evaluate(() => JSON.parse(localStorage.getItem('chemistreal:lessons') || '{}').lessons.length), 0);
    await p6.close();
  }

  chk('콘솔에 예외가 없다', errs.filter(e => !/Failed to fetch|ERR_/.test(e)), []);
  await b.close();
  console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
  process.exit(fail ? 1 : 0);
})();
