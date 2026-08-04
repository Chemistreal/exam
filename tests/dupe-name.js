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
    pending: { ok: true, pending: { active: [] } },
    passed: { ok: true, passed: { passed: [
      { name: '김지완', school: '내정중', course: 'ch1', round: 9,
        attempt: '정시', tries: 1, score: 92, date: '8/1', days: 2 } ] } },
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
