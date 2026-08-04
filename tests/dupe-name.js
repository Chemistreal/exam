/* ============================================================
   같은 반에 이름이 같은 학생 둘
   ------------------------------------------------------------
   화학1 일6-10 반에 **김지완(내정중)** 과 **김지완(대청중)** 두 학생이 있다.

   여태 DT 명단은 이름 글자열의 배열이라 둘을 구분할 수 없었다. 그래서
   한 명만 등록돼 있었고, 그 결과

     · 반 인원이 한 명 모자랐다
     · 한 명이 시험을 보면 **둘 다 응시한 것**이 되어 미응시 문자가 안 나갔다
     · 한 명에게 문자를 보냈다고 표시하면 다른 한 명도 보낸 것으로 보였다

   이제 명단 칸이 `{ n: 이름, s: 학교 }` 를 들 수 있고, DT 가 미응시 목록에
   학교를 같이 보낸다(`absentWho`).

   ⚠ 여기서 제일 중요한 것: **학교는 가르는 데만 쓴다.** 학부모에게 가는
     문자는 예전 그대로 `김지완 학생` 이다 — `김지완 내정중 학생` 이 아니다.
     문구는 `c.absent[j]` 를 이름으로 그대로 쓰므로, 그 값이 순수한 이름인지
     여기서 못박는다.

   실행:
       NODE_PATH=tests/node_modules node tests/dupe-name.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const { spawn } = require('child_process');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8945);
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

/* 내정중 김지완은 9회를 봤고, 대청중 김지완은 안 봤다. */
function part(a) {
  const S = (n, sc, y) => ({ name: n, school: sc, year: y });
  const map = {
    names: { ok: true, classes: [
      { label: '화학1 일6-10', course: 'ch1', kind: 'dt', students: [
        S('김지완', '내정중', '2'),
        S('김지완', '대청중', '2'),
        S('홍길동', '휘문중', '2') ] } ] },
    /* 옛 배포는 이름 칸에 학교가 붙은 채로 보낸다. 그때도 문자는 이름만
       나가야 한다 — 실제로 '김지완 대청중 학생' 이라고 나갔다. */
    _dirty: true,
    pending: { ok: true, pending: { active: [] } },
    /* 선생님이 알려 주신 사실: **7회는 내정중이 봤고 대청중은 안 봤다.**
       9회도 내정중만 통과. 그리고 학교를 안 적고 낸 옛 기록이 하나 있다 —
       그건 누구 것인지 알 길이 없다. */
    passed: { ok: true, passed: { passed: [
      { name: '김지완', school: '내정중', course: 'ch1', round: 7,
        attempt: '정시', tries: 1, score: 88, date: '7/20', days: 15 },
      { name: '김지완', school: '내정중', course: 'ch1', round: 9,
        attempt: '정시', tries: 1, score: 92, date: '8/1', days: 2 },
      { name: '김지완', school: '', course: 'ch1', round: 5,
        attempt: '정시', tries: 1, score: 80, date: '7/6', days: 29 } ] } },
    absentees: { ok: true, absentees: { classes: [
      { label: '화학1 일6-10', course: 'ch1', round: 9, total: 3, present: 1,
        /* DT 가 새로 같이 보내는 것 — 이름 목록은 예전 그대로다. */
        absent: ['김지완', '홍길동'],
        absentWho: [{ name: '김지완', school: '대청중' },
                    { name: '홍길동', school: '휘문중' }] } ] } },
    cohortmis: { ok: true, rows: [] },
    sentlog: { ok: true, sent: [] }, snoozelog: { ok: true, snoozed: [] },
    views: { ok: true, views: [] }, mistags: { ok: true, mis: { rows: [] } },
  };
  return map[a] || { ok: true };
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

  const browser = seal(await chromium.launch(Object.assign(
    { args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));

  try {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 },
                                           serviceWorkers: 'block' });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
    await p.addInitScript(() => {
      try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
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
    await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(2600);

    console.log('── 반 명단 ──');
    const roster = await p.evaluate(() => {
      const cls = dtClassList()[0] || {};
      return { n: (cls.students || []).length,
               kims: (cls.students || []).filter(s => s.name === '김지완')
                       .map(s => s.school) };
    });
    chk('반 인원에 두 명이 다 선다', roster.n, 3);
    chk('학교로 갈린다', roster.kims.sort(), ['내정중', '대청중']);

    console.log('\n── 누가 안 봤는가 ──');
    const st = await p.evaluate(() => {
      const cls = dtClassList()[0];
      return classRows(cls).map(r => ({ name: r.who.name, school: r.who.school,
                                        st: r.st, abs: r.abs.length }));
    });
    st.forEach(r => console.log(`  ${r.name} ${r.school} → ${r.st}`));
    const kim = n => st.filter(r => r.name === '김지완' && r.school === n)[0] || {};
    /* 시험을 본 쪽은 통과, 안 본 쪽은 미응시. 여태는 이름만으로 맞춰 보느라
       한 명이 보면 둘 다 본 것이 됐다. */
    chk('본 김지완(내정중)은 통과', kim('내정중').st, 'ok');
    chk('안 본 김지완(대청중)은 미응시', kim('대청중').st, 'miss');
    chk('미응시 줄이 한 명에게만 붙는다',
        [kim('내정중').abs, kim('대청중').abs], [0, 1]);

    console.log('\n── 이미 쌓인 기록이 각자에게 붙는가 ──');
    const rec = await p.evaluate(() => {
      const of = sc => {
        const r = { name: '김지완', school: sc, grade: '2' };
        const d = dtForStudent(r);
        return { pass: d.passed.map(i => PASS_ROWS[i].round).sort((a, b) => a - b),
                 abs: d.absent.length };
      };
      return { nae: of('내정중'), dae: of('대청중'), orphan: orphanRows() };
    });
    console.log('  내정중 통과 회차 ' + JSON.stringify(rec.nae.pass));
    console.log('  대청중 통과 회차 ' + JSON.stringify(rec.dae.pass));
    /* 여기가 무너지면 7회를 안 본 대청중 김지완이 본 것으로 뜬다. */
    chk('7회는 내정중에게만 붙는다', rec.nae.pass.indexOf(7) >= 0, true);
    chk('대청중에게는 7회가 안 붙는다', rec.dae.pass.indexOf(7) < 0, true);
    chk('9회도 내정중에게만', [rec.nae.pass.indexOf(9) >= 0, rec.dae.pass.indexOf(9) >= 0],
        [true, false]);
    /* 학교를 안 적은 옛 기록(5회)은 **어느 쪽에도 안 붙는다.**
       schoolAkin 은 한쪽이 비면 같은 사람으로 보는데, 김지완이 둘이면
       그 규칙이 한 기록을 두 사람에게 다 붙인다. */
    chk('학교 없는 옛 기록은 아무에게도 안 붙는다',
        [rec.nae.pass.indexOf(5) >= 0, rec.dae.pass.indexOf(5) >= 0], [false, false]);
    /* 대신 말없이 사라지면 안 된다 — 세어서 화면에 띄운다. */
    chk('주인 못 정한 기록을 짚어 준다',
        rec.orphan.map(o => o.kind + ' ' + o.round), ['통과 5']);

    console.log('\n── 문자에 실리는 이름 ──');
    const msg = await p.evaluate(() => {
      const c = ABS_ROWS[0] || {};
      /* copyMsg 가 absentMsg 에 넘기는 값이 바로 이것이다. */
      return { names: c.absent, who: (c.absentWho || []).map(w => w.school) };
    });
    /* ⚠ 여기가 무너지면 학부모에게 '김지완 내정중 학생' 또는
       '[object Object] 학생' 이라고 나간다. */
    chk('문자에 실리는 이름은 순수한 이름', msg.names, ['김지완', '홍길동']);
    chk('학교는 옆에 따로 온다', msg.who, ['대청중', '휘문중']);

    /* 이름 칸에 학교가 붙어 들어와도 문구에는 이름만 실려야 한다.
       선생님이 실제로 받으신 문자가 이랬다:
         [다원교육 영재관 · 화학] **김지완 대청중 학생** 시험 안내 */
    const washed = await p.evaluate(() => [
      justName('김지완 대청중'), justName('김지완(내정중)'),
      justName('김지완 내정중학교'), justName('김지완'),
      justName('김지완대청중'),        // 붙여 쓴 것은 안 가른다
      justName('김 지완'),             // 남는 이름이 짧으면 안 가른다
    ]);
    chk('이름 칸의 학교를 씻어 낸다', washed,
        ['김지완', '김지완', '김지완', '김지완', '김지완대청중', '김 지완']);

    console.log('\n── 보냄 표시 ──');
    const keys = await p.evaluate(() => {
      const c = ABS_ROWS[0];
      return (c.absent || []).map((nm, j) =>
        sentKey('abs', nm, c.course, c.round, absSchool(c, j)));
    });
    /* 두 김지완이 한 열쇠를 나눠 쓰면, 한 명에게 보냈다고 표시하는 순간
       다른 한 명도 보낸 것으로 보인다. */
    chk('학교가 열쇠에 섞인다', /대청중$/.test(keys[0]), true);
    chk('열쇠가 서로 다르다', keys[0] !== keys[1], true);

    chk('콘솔에 예외가 없다', errs, []);
    await ctx.close();
  } finally {
    await browser.close();
    srv.kill();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
