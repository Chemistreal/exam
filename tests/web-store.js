/* ============================================================
   웹이 원본, 브라우저는 사본 (브라우저 필요 — CI 에서는 저절로 건너뛴다)
   ------------------------------------------------------------
   기록은 구글 시트에 다 있었다. 그런데 화면에 뜨는 것은 늘 **이 브라우저에
   남은 것**뿐이었다. 받아오려면 버튼을 눌러야 했고, 그 버튼은 회차마다 한 번씩
   서른여덟 번을 물어서 최악이면 7분 반이 걸렸다. 그래서 아무도 안 눌렀다.

   학원 PC 와 노트북에서 반씩 채점하면 양쪽 다 절반씩만 알았다. 어느 쪽 화면도
   사실이 아니었는데, 화면은 그 사실을 말하지 않았다.

   여기서 지키는 것:
   - 한 번에 받는다(action=all). 회차 수만큼 부르지 않는다
   - 열 때마다 저절로 맞춘다. 사람이 기억해야 맞는 것은 안 맞는다
   - 그렇다고 화면을 갈아엎지 않는다 — 답안을 입력하던 중이면 건드리지 않는다
   - 못 보낸 기록은 다시 보낸다. no-cors POST 는 성공을 알 수 없으니,
     시트를 다시 읽어 그 줄이 보이는지로 확인한다
   - 다만 한없이 다시 보내지는 않는다(같은 줄이 시트에 쌓인다)
   - 시트에서 온 기록은 되돌려 보내지 않는다(지운 줄이 되살아난다)
   - 시트에서 없어진 줄은 여기서도 없앤다. 안 그러면 다른 기기에서 지운 학생이
     계속 보이고, 이름을 고친 학생은 두 명이 된다
   - 그래도 시트가 한 번도 가진 적 없는 줄은 지키다(되돌릴 수 없다)
   - 학부모가 연 공유 링크에서는 아무것도 받지도 보내지도 않는다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/web-store.js
   ============================================================ */
'use strict';
/* 멈추는 검사는 실패하는 검사보다 나쁘다 — tests/_watchdog.js 주석 참고. */
require('./_watchdog.js')(240);
/* 검사가 진짜 시트에 쓰면 안 된다. 실제로 CI 가 돌 때마다 파이널 앱이
   진짜 앱스크립트로 제출해서, 홍길동·예비본 같은 줄이 학생들 석차
   모집단에 섞여 들어갔다. 브라우저를 띄우자마자 그 길을 끊는다. */
const seal = require('./_seal.js');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
const HUB = fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* ── 0부. 시트 쪽 (브라우저 없이) ─────────────────────────────────────── */
console.log('── 시트가 전부를 한 번에 준다 ──');
{
  chk('all 창구가 열려 있다', /p\.action === 'all'\) return allRows_\(cb\)/.test(GAS), true);
  chk('한 학생만 뽑을 때와 같은 자리를 읽는다',
      /function historyFor_[\s\S]{0,400}_recordRows_\(key\)/.test(GAS), true);
  chk('전부 뽑을 때도 같은 자리', /function allRows_[\s\S]{0,200}_recordRows_\(''\)/.test(GAS), true);
  // 이름을 안 주면 거르지 않는다 — 여기가 뒤집히면 all 이 빈 배열을 준다
  chk('이름이 없으면 전부', /if \(key && _histKey_\(r\[1\]\) !== key\) continue;/.test(GAS), true);
  // 앱은 id 로 회차를 찾는다. 제목만 주면 한 건도 못 붙인다
  chk('행마다 회차 id 를 붙여 준다', /examId: eid/.test(GAS), true);
  chk('표에 없는 제목은 뺀다', /if \(!eid\) continue;/.test(GAS), true);
  chk('학교·학년도 함께', /school: String\(r\[6\][\s\S]{0,60}grade: String\(r\[7\]/.test(GAS), true);

  const rec = GAS.slice(GAS.indexOf('function _recordRows_'), GAS.indexOf('function _jsonOut_'));
  chk('_recordRows_ 는 한 벌뿐',
      (GAS.match(/function _recordRows_/g) || []).length, 1);
  chk('읽기가 실패해도 빈 배열을 준다', /catch \(err\) \{\}[\s\S]{0,40}return out;/.test(rec), true);
}

console.log('\n── 통합 셸도 같은 주기로 맞춘다 ──');
{
  chk('셸의 묵힘 기준이 짧아졌다', /const SYNC_STALE = 10\*60\*1000;/.test(HUB), true);
  chk('셸은 여전히 쓰지 않는다(파이널에 시킨다)',
      /w\.syncAllFromSheet\(res, true\)/.test(HUB), true);
}

console.log('\n── 소스가 지켜야 하는 것 ──');
{
  const strip = SRC.replace(/\/\*[\s\S]*?\*\//g, '');
  chk('한 번에 받는 길이 있다', /function syncOneShot\(/.test(strip), true);
  chk('시트 쪽이 옛 판이면 회차별로 되돌아간다', /syncPerExam\(onDone, quiet\)/.test(strip), true);
  chk('보낼 줄을 만드는 자리는 한 곳',
      (strip.match(/function sheetPayloadFor\(/g) || []).length, 1);
  chk('채점 직후와 재전송이 그 한 곳을 쓴다',
      (strip.match(/sheetPayloadFor\(/g) || []).length >= 3, true);
  // 동기화가 끝났다고 화면을 갈아엎으면 입력하던 답안이 날아간다
  chk('동기화 뒤에는 refreshScreen 으로 그린다',
      /function syncAllFromSheet[\s\S]{0,900}refreshScreen\(\)/.test(strip), true);
  chk('채점 중이면 다시 그리지 않는다',
      /function refreshScreen\(\)\{[\s\S]{0,200}if\(cur\) return;/.test(strip), true);
}

/* ── 브라우저 ────────────────────────────────────────────────────────── */
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const U = `http://localhost:${PORT}/final.html`;

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
  console.log('\n건너뜀: playwright 를 찾지 못했다 (PLAYWRIGHT_MODULE 로 경로 지정)');
  console.log(fail ? `\n${fail}개 실패` : '\n소스 검사는 모두 통과');
  process.exit(fail ? 1 : 0);
}

const A60 = c => String(c).repeat(60);
/* 시트를 가로챈다. 무엇을 몇 번 물었는지, 무엇을 보냈는지 센다. */
function stubSheet(page, state) {
  return page.route('**/macros/s/**', route => {
    const req = route.request();
    if (req.method() === 'POST') {
      state.posts.push(JSON.parse(req.postData() || '{}'));
      if (state.acceptPost) state.rows.push(state.acceptPost(JSON.parse(req.postData() || '{}')));
      return route.fulfill({ status: 200, body: '{}' });
    }
    const u = new URL(req.url());
    const act = u.searchParams.get('action'), cb = u.searchParams.get('callback');
    state.calls.push(act);
    if (state.dead) return route.fulfill({ status: 500, body: '' });
    let body = { ok: true };
    if (act === 'all') body = { ok: true, n: state.rows.length, rows: state.rows.slice() };
    else if (act === 'history') body = { ok: true, rows: [] };
    else if (act === 'list') body = { ok: true, students: [] };
    return route.fulfill({ status: 200, contentType: 'application/javascript',
                           body: cb + '(' + JSON.stringify(body) + ')' });
  });
}
const row = (name, ans, extra) => Object.assign({
  examId: 'jmchc-1', exam: 'JMChC 1회', name: name, school: 'A중', grade: '3',
  answers: ans, ts: Date.UTC(2026, 2, 1),
}, extra || {});

async function oneCall(browser, errs) {
  console.log('\n── 열면 한 번에 받는다 ──');
  const st = { calls: [], posts: [], rows: [row('김서준', A60(1)), row('이하윤', A60(2))] };
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('한번에: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);

  const got = await p.evaluate(() => ({
    subs: subs('jmchc-1').map(r => r.name + ':' + r.up),
    synced: lastSyncAt() > 0,
    listed: document.body.innerText.includes('JMChC'),
  }));
  console.log('  물어본 것:', JSON.stringify(st.calls));
  // 회차가 서른여덟 개다. 회차마다 물으면 여기가 38 이 된다 — 그래서 아무도 안 눌렀다
  chk('시트에 딱 한 번 묻는다', st.calls.filter(c => c === 'all').length, 1);
  chk('회차별로 묻지 않는다', st.calls.filter(c => c === 'list').length, 0);
  chk('아무도 안 눌렀는데 받아 왔다', got.subs, ['김서준:1', '이하윤:1']);
  chk('맞춘 시각이 남았다', got.synced, true);
  chk('시트에서 온 것은 올릴 것이 없다(up:1)', got.subs.every(s => s.endsWith(':1')), true);
  chk('되돌려 보내지 않는다', st.posts.length, 0);

  // 방금 맞췄으니 곧바로 다시 열어도 안 묻는다
  st.calls.length = 0;
  await p.reload({ waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  chk('금방 다시 열면 안 묻는다', st.calls.length, 0);

  // 묵으면 다시 묻는다
  st.calls.length = 0;
  await p.evaluate(() => localStorage.setItem('chemistreal:final:lastsync', String(Date.now() - 40 * 60 * 1000)));
  await p.reload({ waitUntil: 'networkidle' });
  await p.waitForTimeout(2000);
  chk('묵으면 다시 묻는다', st.calls.filter(c => c === 'all').length, 1);
  await p.close();
}

async function pendingUpload(browser, errs) {
  console.log('\n── 못 보낸 기록은 다시 보낸다 ──');
  const st = { calls: [], posts: [], rows: [] };
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('재전송: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);

  const scored = await p.evaluate(async () => {
    openExam('jmchc-1');
    document.getElementById('nm').value = '박하람';
    document.getElementById('sch').value = 'C중';
    for (let q = 1; q <= cur.nQ; q++) setAns(q, 3);
    scoreAuto();
    await new Promise(r => setTimeout(r, 1200));
    return subs('jmchc-1').map(r => r.name + ':' + r.up);
  });
  chk('채점하면 아직 확인 못 함(up:0)', scored, ['박하람:0']);
  chk('그때 한 번 보냈다', st.posts.length, 1);
  chk('보낸 답안이 맞다', st.posts[0] && st.posts[0].answers, A60(3));
  chk('보낸 이름·학교도 맞다', [st.posts[0].name, st.posts[0].school], ['박하람', 'C중']);

  // 시트에 안 보이면 다시 보낸다
  const resync = async () => p.evaluate(() => new Promise(res => {
    localStorage.setItem('chemistreal:final:lastsync', '0');
    syncAllFromSheet(() => setTimeout(() => res(subs('jmchc-1').map(r => r.name + ':' + r.up + '/' + (r.upTry | 0))), 600), true);
  }));
  st.posts.length = 0;
  let s2 = await resync();
  chk('시트에 없으면 다시 보낸다', st.posts.length, 1);
  chk('보낸 횟수를 센다', s2, ['박하람:0/1']);

  st.posts.length = 0; await resync();
  st.posts.length = 0; const s4 = await resync();
  chk('세 번까지만 보낸다', s4, ['박하람:0/3']);
  st.posts.length = 0; const s5 = await resync();
  // 계속 보내면 시트에 같은 줄이 쌓인다. 멈추고 표시만 남긴다.
  chk('네 번째는 안 보낸다', st.posts.length, 0);
  chk('멈췄다는 표시가 남는다', s5, ['박하람:2/3']);
  await p.close();
}

async function confirmed(browser, errs) {
  console.log('\n── 시트에서 보이면 표를 지운다 ──');
  const st = { calls: [], posts: [], rows: [] };
  // 보낸 것이 실제로 시트에 꽂히는 상황
  st.acceptPost = d => row(d.name, d.answers, { school: d.school, grade: d.grade });
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('확인: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);

  const after = await p.evaluate(async () => {
    openExam('jmchc-1');
    document.getElementById('nm').value = '최유나';
    document.getElementById('sch').value = 'D중';
    for (let q = 1; q <= cur.nQ; q++) setAns(q, 4);
    scoreAuto();
    await new Promise(r => setTimeout(r, 1200));
    const before = subs('jmchc-1').map(r => r.name + ':' + r.up);
    return new Promise(res => {
      localStorage.setItem('chemistreal:final:lastsync', '0');
      syncAllFromSheet(() => setTimeout(() =>
        res({ before: before, after: subs('jmchc-1').map(r => r.name + ':' + r.up + '/' + (r.upTry | 0)) }), 600), true);
    });
  });
  chk('보내기 전에는 미확인', after.before, ['최유나:0']);
  // 여기가 이 장치의 핵심이다 — no-cors 는 성공을 알려 주지 않으므로
  // 시트를 다시 읽어 그 줄이 보이는 것으로만 확인할 수 있다
  chk('시트에서 보이면 확인 처리', after.after, ['최유나:1/0']);
  chk('다시 보내지 않았다', st.posts.length, 1);
  await p.close();
}

/* ── 다른 기기에서 지우거나 고친 것이 여기까지 온다 ──────────────────────
   사본이 **더하기만** 하고 있었다. 학원 PC 에서 학생을 지우면 시트는 고쳐지는데
   노트북에는 옛 줄이 그대로 남았고, 이름을 고치면 옛 이름 줄이 남은 채 새 이름
   줄이 시트에서 들어와 **한 학생이 두 명**이 됐다. */
async function pruneGone(browser, errs) {
  console.log('\n── 시트에서 없어진 줄은 여기서도 없어진다 ──');
  const st = { calls: [], posts: [],
               rows: [row('김서준', A60(1)), row('이하윤', A60(2)), row('박민준', A60(3))] };
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('정리: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  const first = await p.evaluate(() => subs('jmchc-1').map(r => r.name));
  chk('셋 다 받았다', first, ['김서준', '이하윤', '박민준']);

  const resync = () => p.evaluate(() => new Promise(res => {
    localStorage.setItem('chemistreal:final:lastsync', '0');
    syncAllFromSheet(r => setTimeout(() => res({ r: r, names: subs('jmchc-1').map(x => x.name) }), 500), true);
  }));

  // 다른 기기에서 박민준을 지웠다
  st.rows = st.rows.filter(r => r.name !== '박민준');
  const del = await resync();
  chk('지운 학생이 여기서도 사라진다', del.names, ['김서준', '이하윤']);
  chk('몇 건을 정리했는지 알린다', del.r.dropped, 1);

  // 다른 기기에서 이하윤 → 이하윤(고침) 으로 이름을 고쳤다
  st.rows = st.rows.map(r => r.name === '이하윤' ? Object.assign({}, r, { name: '이하윤고침' }) : r);
  const ren = await resync();
  // 여기가 뒤집히면 한 학생이 두 명이 된다 — 옛 이름 줄이 안 없어지기 때문이다
  chk('이름을 고치면 한 명 그대로', ren.names, ['김서준', '이하윤고침']);

  // 시트 읽기가 엎어져도 {ok:true, rows:[]} 로 온다. 그걸 '전부 지워졌다' 로
  // 읽으면 이 브라우저 기록이 통째로 날아간다.
  st.rows = [];
  const empty = await resync();
  chk('빈 응답에 기록을 지우지 않는다', empty.names, ['김서준', '이하윤고침']);
  chk('그때는 정리했다고 하지 않는다', empty.r.dropped, 0);

  /* 다른 회차 줄만 왔을 때도 마찬가지다. 응답에 그 회차가 없는 것은
     '그 회차가 비었다' 가 아니라 '모른다' 다. */
  st.rows = [row('남의회차학생', A60(1), { examId: 'jmchc-2', exam: 'JMChC 2회' })];
  const other = await resync();
  chk('다른 회차만 왔을 때도 안 지운다', other.names, ['김서준', '이하윤고침']);
  chk('그때도 정리하지 않는다', other.r.dropped, 0);
  await p.close();
}

/* 아직 못 올린 줄과 출처를 모르는 옛 줄은 시트에 없어도 지우지 않는다.
   시트가 한 번도 가진 적 없는 기록을 지우면 되돌릴 수 없다. */
async function keepUnconfirmed(browser, errs) {
  console.log('\n── 시트가 가진 적 없는 줄은 지키다 ──');
  const st = { calls: [], posts: [], rows: [row('김서준', A60(1))] };
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('지키기: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2000);

  const got = await p.evaluate(() => {
    // 출처를 모르는 옛 줄(up 없음) 하나를 손으로 끼워 넣는다
    const arr = subs('jmchc-1');
    arr.push({ name: '옛기록', school: 'Z중', grade: '1', ts: 1,
               correct: 0, total: 60, wrong: 60, ans: new Array(60).fill(4) });
    saveSubs('jmchc-1', arr);
    return new Promise(res => {
      localStorage.setItem('chemistreal:final:lastsync', '0');
      syncAllFromSheet(r => setTimeout(() => res({
        r: r, names: subs('jmchc-1').map(x => x.name + ':' + (x.up === undefined ? '-' : x.up)),
      }), 500), true);
    });
  });
  chk('출처를 모르는 옛 줄은 남는다', got.names.indexOf('옛기록:-') >= 0, true);
  chk('시트에서 온 줄은 확인 표시', got.names.indexOf('김서준:1') >= 0, true);
  chk('지운 것이 없다', got.r.dropped, 0);
  await p.close();
}

async function neverClobber(browser, errs) {
  console.log('\n── 입력 중인 화면을 갈아엎지 않는다 ──');
  const st = { calls: [], posts: [], rows: [row('김서준', A60(1))] };
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('갈아엎기: ' + e.message));
  await stubSheet(p, st);
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2000);

  const kept = await p.evaluate(() => new Promise(res => {
    openExam('jmchc-1');
    document.getElementById('nm').value = '입력중인학생';
    for (let q = 1; q <= 20; q++) setAns(q, 2);
    const marked = () => Object.keys(sel).filter(q => sel[q]).length;
    const was = marked();
    localStorage.setItem('chemistreal:final:lastsync', '0');
    syncAllFromSheet(() => setTimeout(() => res({
      was: was, now: marked(),
      nameBox: !!document.getElementById('nm'),
      name: (document.getElementById('nm') || {}).value,
    }), 400), true);
  }));
  // 열 때마다 저절로 도는 장치라, 여기가 뒤집히면 채점하던 답안이 통째로 날아간다
  chk('입력칸이 그대로 있다', kept.nameBox, true);
  chk('입력한 이름이 그대로', kept.name, '입력중인학생');
  chk('표시한 답안이 그대로', [kept.was, kept.now], [20, 20]);
  await p.close();
}

async function sharedLinkQuiet(browser, errs) {
  console.log('\n── 학부모 링크에서는 아무것도 안 한다 ──');
  const st0 = { calls: [], posts: [], rows: [row('김서준', A60(1))] };
  const teacher = await browser.newPage();
  teacher.on('pageerror', e => errs.push('교사: ' + e.message));
  await stubSheet(teacher, st0);
  await teacher.goto(U, { waitUntil: 'networkidle' });
  await teacher.waitForTimeout(1500);
  const link = await teacher.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-1'), s = {};
    for (let q = 1; q <= ex.nQ; q++) s[q] = ex.key[q - 1] || 1;
    return shareLinkFinal(ex, s, '홍길동', '');
  });
  await teacher.close();

  const st = { calls: [], posts: [], rows: [row('김서준', A60(1))] };
  const parent = await browser.newPage();
  parent.on('pageerror', e => errs.push('학부모: ' + e.message));
  await stubSheet(parent, st);
  await parent.goto(link, { waitUntil: 'networkidle' });
  await parent.waitForTimeout(2500);
  // 학부모 폰에 남의 성적을 받아 둘 이유가 없다. 성적표에 필요한 것은
  // 링크에 이미 다 들어 있다.
  chk('전체를 받아 오지 않는다', st.calls.filter(c => c === 'all').length, 0);
  chk('시트로 보내지도 않는다', st.posts.length, 0);
  chk('그래도 성적표는 나온다', await parent.evaluate(() => (window.__rpt || {}).name || ''), '홍길동');
  await parent.close();
}

async function oldSheetFallback(browser, errs) {
  console.log('\n── 시트 쪽이 아직 옛 판이면 ──');
  const p = await browser.newPage();
  p.on('pageerror', e => errs.push('되돌아가기: ' + e.message));
  const calls = [];
  // all 을 모르는 옛 배포: {ok:false} 를 준다
  await p.route('**/macros/s/**', route => {
    const req = route.request();
    if (req.method() === 'POST') return route.fulfill({ status: 200, body: '{}' });
    const u = new URL(req.url());
    const act = u.searchParams.get('action'), cb = u.searchParams.get('callback');
    calls.push(act);
    const body = act === 'all' ? { ok: false, error: 'unknown action' }
               : act === 'list' ? { ok: true, students: [{ name: '옛길학생', school: 'E중', grade: '1', answers: A60(1), ts: 1 }] }
               : { ok: true, rows: [] };
    return route.fulfill({ status: 200, contentType: 'application/javascript',
                           body: cb + '(' + JSON.stringify(body) + ')' });
  });
  await p.goto(U, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1200);
  const got = await p.evaluate(() => new Promise(res => {
    localStorage.setItem('chemistreal:final:lastsync', '0');
    syncAllFromSheet(r => res({ r: r, n: subs('jmchc-1').length }), true);
  }));
  chk('한 번에 받기를 먼저 시도한다', calls[0], 'all');
  chk('안 되면 회차별로 되돌아간다', calls.filter(c => c === 'list').length > 1, true);
  chk('되돌아가서도 받아 온다', got.n >= 1, true);
  await p.close();
}

(async () => {
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  const errs = [];
  await oneCall(browser, errs);
  await pendingUpload(browser, errs);
  await confirmed(browser, errs);
  await pruneGone(browser, errs);
  await keepUnconfirmed(browser, errs);
  await neverClobber(browser, errs);
  await sharedLinkQuiet(browser, errs);
  await oldSheetFallback(browser, errs);
  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
