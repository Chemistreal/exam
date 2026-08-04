/* ============================================================
   시트 수정 창구 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   이름을 잘못 입력했을 때 앱에서 고쳐도 구글 시트에는 옛 이름 행이 그대로
   남았다. 그러면 '시트에서 불러오기'가 그 행을 **다른 사람**으로 보고 다시
   넣고(중복 판정이 이름+답안이라서), 성적문자도 옛 이름으로 나간다.

   그래서 시트를 직접 고치는 창구를 열었다. 행을 지우는 일이 섞이므로
   조심할 곳이 많다.

   열쇠(동기화 키)는 선생님 요청으로 없앴다. **이 URL 을 아는 사람은 누구나**
   읽고 쓴다. 그러면 남는 안전장치는 "행을 정확히 지목해야만 바뀐다" 하나뿐이라,
   지목이 얼마나 정확한지가 훨씬 중요해졌다.

   여기서 지키는 것:
   - 열쇠 흔적이 남아 있지 않다(반만 지워 조용히 막히는 상태가 가장 나쁘다)
   - 통째로 비우는 동작이 없다 — 지우려면 반드시 행을 지목해야 한다
   - 이름 일괄 고치기와 학생 삭제는 전 시험에 닿는다
   - 한 줄 고치기·지우기는 시험+이름+답안이 **다 맞는 행만** 건드린다
   - 학교·학년을 함께 주면 동명이인 중 한쪽만 건드린다
   - 겹친 줄 정리는 학교·학년이 적힌 쪽을 남긴다
   - 여러 줄을 지울 때 뒤에서부터 지운다(앞에서 지우면 행 번호가 밀린다)
   - 고친 뒤 성적문자 탭을 다시 만든다

   실행:  node tests/sheet-edit.js
   ============================================================ */
'use strict';
const GAS_ENV = require('./_gasenv.js');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* 시트 흉내. 실제 스프레드시트는 못 띄우니 필요한 만큼만 만든다.
   행 번호는 1부터, 데이터는 2행부터 — 진짜와 같게 맞춰야 삭제 순서 같은
   실수가 여기서 걸린다. */
function fakeSheet(rows) {
  const grid = rows.map(r => r.slice());
  let messagesRebuilt = 0;
  const sheet = {
    _grid: grid,
    getLastRow: () => grid.length + 1,          // 머리글 1행 + 데이터
    getRange(row, col, nRow, nCol) {
      nRow = nRow || 1; nCol = nCol || 1;
      return {
        getValues: () => { const out = [];
          for (let i = 0; i < nRow; i++) { const src = grid[row - 2 + i] || [], line = [];
            for (let j = 0; j < nCol; j++) line.push(src[col - 1 + j]);
            out.push(line); }
          return out; },
        setValues(vals) { for (let i = 0; i < vals.length; i++)
          for (let j = 0; j < vals[i].length; j++) grid[row - 2 + i][col - 1 + j] = vals[i][j]; },
        setValue(v) { grid[row - 2][col - 1] = v; },
      };
    },
    deleteRow(r) { grid.splice(r - 2, 1); },
    _rebuilt: () => messagesRebuilt,
    _bump: () => { messagesRebuilt++; },
  };
  return sheet;
}

function load(sheet) {
  const gas = {
    Logger: { log() {} },
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ({ getSheetByName: () => sheet }),
      flush() {},
    },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    ContentService: {
      MimeType: { JSON: 'json', JAVASCRIPT: 'js' },
      createTextOutput: t => ({ _t: t, setMimeType() { return this; } }),
    },
    Utilities: { formatDate: GAS_ENV.formatDate },
    Session: { getScriptTimeZone: () => 'Asia/Seoul' },
    PropertiesService: { getScriptProperties: () => ({ getProperty: () => '' }) },
  };
  vm.createContext(gas);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'AppsScript-Code.gs'), 'utf8'), gas);
  // 성적문자 재생성은 시트 전체를 건드리므로 세었는지만 본다
  gas.fillReportMessages = () => sheet._bump();
  return gas;
}

// [0시험 1이름 2링크 3저장시각 4수험번호 5응시일 6학교 7학년 …16답안]
const R = (exam, name, school, grade, ans) => {
  const r = new Array(17).fill('');
  r[0] = exam; r[1] = name; r[6] = school; r[7] = grade; r[16] = "'" + ans;
  return r;
};
const A1 = '1'.repeat(60), A2 = '2'.repeat(60), A3 = '3'.repeat(60);
const T6 = 'JMChC 모의고사 6회', T7 = 'JMChC 모의고사 7회';
const seed = () => [
  R(T6, '김지 성', 'X중', '2', A1),
  R(T6, '이도현', 'Y중', '3', A2),
  R(T6, '김지 성', 'X중', '2', A3),   // 같은 이름·다른 답안 — 한 줄 지우기가 이걸 건드리면 안 된다
  R(T7, '김지 성', 'X중', '2', A1),   // 다른 시험·같은 이름·같은 답안
];
const names = sh => sh._grid.map(r => r[1]);

console.log('── 열쇠 없이 통한다 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'rename', from: '김지 성', to: '김지성' } })._t);
  chk('키 없이 고쳐진다', [out.ok, out.changed], [true, 3]);
}
{
  // 열쇠를 반만 지우면 최악이다 — 앱은 키를 안 보내는데 시트만 요구해서
  // 아무 반응 없이 실패한다. 코드에 흔적이 남았는지 본다.
  const src = fs.readFileSync(path.join(__dirname, '..', 'AppsScript-Code.gs'), 'utf8');
  chk('_keyOk 가 없다', /_keyOk/.test(src), false);
  chk('SECRET 을 읽지 않는다', /getProperty\(\s*'SECRET'\s*\)/.test(src), false);
  chk('unauthorized 응답이 없다', /'unauthorized'/.test(src), false);
}

console.log('\n── 지목하지 않으면 아무것도 안 지운다 ──');
{
  // 열쇠가 없어진 뒤로는 이것이 유일한 안전장치다.
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const noName = JSON.parse(gas.doGet({ parameter: { action: 'deleteRow', exam: 'jmchc-6', answers: A1 } })._t);
  chk('이름 없이는 못 지운다', noName.error, 'bad-args');
  const noAns = JSON.parse(gas.doGet({ parameter: { action: 'deleteRow', exam: 'jmchc-6', name: '김지 성' } })._t);
  chk('답안 없이는 못 지운다', noAns.error, 'bad-args');
  const wrong = JSON.parse(gas.doGet({ parameter: { action: 'deleteRow', exam: 'jmchc-6', name: '김지 성',
    answers: '4'.repeat(60) } })._t);
  chk('답안이 어긋나면 0건', wrong.changed, 0);
  chk('행이 하나도 안 없어졌다', sh._grid.length, 4);
  // '전부 지우기' 같은 동작을 실수로도 만들지 않았는지
  chk('시트를 통째로 비우는 동작이 없다',
      /clearContents|deleteRows\(|clear\(\)/.test(
        fs.readFileSync(path.join(__dirname, '..', 'AppsScript-Code.gs'), 'utf8')
          .split('function _sheetEdit')[1].split('\nfunction ')[0]), false);
}

console.log('\n── 이름 일괄 고치기 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'rename', from: '김지 성', to: '김지성' } })._t);
  chk('3건 고쳤다', [out.ok, out.changed], [true, 3]);
  chk('전 시험에 닿는다', names(sh), ['김지성', '이도현', '김지성', '김지성']);
  chk('남의 이름은 그대로', names(sh)[1], '이도현');
  chk('성적문자를 다시 만든다', sh._rebuilt(), 1);
  const none = JSON.parse(gas.doGet({ parameter: { action: 'rename', from: '없는사람', to: 'X' } })._t);
  chk('없는 이름이면 0건', none.changed, 0);
  const bad = JSON.parse(gas.doGet({ parameter: { action: 'rename', from: '김지성', to: '' } })._t);
  chk('빈 이름으로는 못 바꾼다', bad.error, 'bad-args');
}

console.log('\n── 한 줄 고치기 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'editRow', exam: 'jmchc-6', name: '김지 성',
    answers: A1, setName: '김지성', setSchool: '대원국제중', setGrade: '3' } })._t);
  chk('한 줄만 바뀐다', out.changed, 1);
  chk('그 줄이 바뀌었다', [sh._grid[0][1], sh._grid[0][6], sh._grid[0][7]], ['김지성', '대원국제중', '3']);
  chk('같은 이름·다른 답안은 그대로', sh._grid[2][1], '김지 성');
  chk('다른 시험 같은 답안도 그대로', sh._grid[3][1], '김지 성');
}

console.log('\n── 한 줄 지우기 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'deleteRow', exam: 'jmchc-6', name: '김지 성',
    answers: A1 } })._t);
  chk('한 줄만 지운다', [out.changed, sh._grid.length], [1, 3]);
  chk('남은 줄', names(sh), ['이도현', '김지 성', '김지 성']);
  chk('다른 시험 줄은 살아 있다', sh._grid[2][0], T7);
}
{
  // 같은 시험·같은 이름·같은 답안이 두 줄이면 둘 다 지운다. 뒤에서부터
  // 지워야 한다 — 앞에서 지우면 남은 행 번호가 밀려 엉뚱한 줄이 날아간다.
  const rows = seed(); rows.splice(2, 0, R(T6, '김지 성', 'X중', '2', A1));
  const sh = fakeSheet(rows);
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'deleteRow', exam: 'jmchc-6', name: '김지 성',
    answers: A1 } })._t);
  chk('겹친 두 줄을 지운다', out.changed, 2);
  /* 이름만 보면 안 된다. 앞에서부터 지우면 남은 줄이 밀려 **다른 답안의
     같은 이름** 줄이 날아가는데, 이름 목록만 비교하면 그게 안 걸린다.
     실제로 그렇게 짜 놓고 검사가 통과하는 것을 보았다. 답안까지 본다. */
  chk('엉뚱한 줄이 안 날아간다', sh._grid.map(r => r[1] + '|' + String(r[16]).slice(1, 2)),
      ['이도현|2', '김지 성|3', '김지 성|1']);
}

console.log('\n── 학생 통째로 지우기 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const bad = JSON.parse(gas.doGet({ parameter: { action: 'deleteName' } })._t);
  chk('이름 없이는 못 지운다', bad.error, 'bad-args');
  chk('행이 그대로', sh._grid.length, 4);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'deleteName', name: '김지 성' } })._t);
  // 시험을 가리지 않는다 — 그 사람의 기록을 전부 없애는 동작이다
  chk('전 시험에서 지운다', out.changed, 3);
  chk('남는 것은 남의 기록뿐', sh._grid.map(r => r[1]), ['이도현']);
  chk('성적문자를 다시 만든다', sh._rebuilt(), 1);
  const none = JSON.parse(gas.doGet({ parameter: { action: 'deleteName', name: '없는사람' } })._t);
  chk('없는 이름이면 0건', none.changed, 0);
  chk('0건일 때 행이 그대로', sh._grid.length, 1);
}
{
  // 여기서도 뒤에서부터 지워야 한다. 앞에서 지우면 남은 행이 밀린다.
  const sh = fakeSheet([
    R(T6, '지울사람', 'X중', '2', A1),
    R(T6, '남을사람', 'Y중', '3', A2),
    R(T7, '지울사람', 'X중', '2', A3),
    R(T7, '남을사람', 'Y중', '3', A1),
  ]);
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'deleteName', name: '지울사람' } })._t);
  chk('띄엄띄엄 있어도 다 지운다', out.changed, 2);
  chk('엉뚱한 줄이 안 날아간다', sh._grid.map(r => r[1] + '|' + String(r[16]).slice(1, 2)),
      ['남을사람|2', '남을사람|1']);
}

console.log('\n── 학교·학년으로 동명이인 가르기 ──');
{
  /* 이름·학교·학년이 모두 같아야 같은 학생이다. school·grade 를 함께 주면
     그 사람의 행만 건드린다 — 안 주면 동명이인까지 같이 바뀐다. */
  const sh = fakeSheet([
    R(T6, '이서준', '과천중', '2', A1),
    R(T6, '이서준', '분당중', '3', A2),
    R(T7, '이서준', '과천중', '2', A3),
  ]);
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'rename', from: '이서준', to: '이서준A',
    school: '과천중', grade: '2' } })._t);
  chk('그 학교·학년만 바뀐다', out.changed, 2);
  chk('동명이인은 그대로', sh._grid.map(r => r[1] + '|' + r[6]),
      ['이서준A|과천중', '이서준|분당중', '이서준A|과천중']);
}
{
  const sh = fakeSheet([
    R(T6, '이서준', '과천중', '2', A1),
    R(T6, '이서준', '분당중', '3', A2),
  ]);
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'deleteName', name: '이서준',
    school: '분당중', grade: '3' } })._t);
  chk('지정한 학생만 지운다', out.changed, 1);
  chk('남는 쪽', sh._grid.map(r => r[6]), ['과천중']);
}

console.log('\n── 겹친 줄 정리 ──');
{
  /* 채점을 두 번 하면 같은 응시가 두 줄로 쌓였다. 시험+이름+답안이 같으면
     같은 응시로 보고 한 줄만 남긴다 — 학교·학년이 적힌 쪽을 살린다. */
  const sh = fakeSheet([
    R(T6, '이서준', '', '', A1),          // 학교·학년이 빈 줄
    R(T6, '이서준', '과천중', '2', A1),   // 같은 응시, 채워진 줄
    R(T6, '이서준', '과천중', '2', A2),   // 답안이 다르다 → 다른 응시
    R(T7, '이서준', '', '', A1),          // 시험이 다르다 → 다른 응시
  ]);
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'dedupe' } })._t);
  chk('한 줄만 지운다', out.changed, 1);
  chk('채워진 줄을 남긴다', sh._grid.map(r => r[0].slice(-2) + '|' + r[6] + '|' + String(r[16]).slice(1, 2)),
      ['6회|과천중|1', '6회|과천중|2', '7회||1']);
  chk('성적문자를 다시 만든다', sh._rebuilt(), 1);
  const again = JSON.parse(gas.doGet({ parameter: { action: 'dedupe' } })._t);
  chk('두 번 돌려도 더 안 지운다', again.changed, 0);
}

console.log('\n── 읽기 ──');
{
  const sh = fakeSheet(seed());
  const gas = load(sh);
  const out = JSON.parse(gas.doGet({ parameter: { action: 'list', exam: 'jmchc-6' } })._t);
  chk('목록이 나온다', out.ok, true);
  chk('열쇠 경고는 이제 없다', out.warning, undefined);
}

/* ── 검사가 남긴 줄만 지운다 ────────────────────────────────────────
   CI 의 브라우저 검사가 진짜 앱스크립트로 제출해서, 학생이 아닌 줄이 시트에
   쌓였다(홍길동 60/60 · 예비본 57/60 …). 그 줄들이 석차 모집단에 들어가
   진짜 학생들의 등수를 밀어냈다.

   손으로 지우면 빠뜨린다 — '이도현' 은 진짜 줄과 검사 줄이 둘 다 있어서
   이름으로는 못 가른다. 가르는 것은 링크다. */
console.log('\n── 검사가 남긴 줄만 지운다 ──');
{
  const GAS = fs.readFileSync(path.join(__dirname, '..', 'AppsScript-Code.gs'), 'utf8');
  const fn = GAS.slice(GAS.indexOf('function _purgeTestRows'));
  const body = fn.slice(0, fn.indexOf('\nfunction ', 10));
  chk('창구가 있다', /p\.action === 'purgeTest'/.test(GAS), true);
  /* 가르는 잣대는 링크 하나뿐이고, 밖에서 바꿀 수 없어야 한다. */
  chk('링크로만 고른다', /localhost\|127\\\.0\\\.0\\\.1\/i\.test\(link\)/.test(body), true);
  chk('조건을 밖에서 못 준다', /p\.(where|match|filter|link)/.test(body), false);
  /* 지우는 것은 되돌릴 수 없다 — 먼저 몇 줄인지 보여 주고, go 를 받아야 지운다. */
  chk('go 없이는 안 지운다', /if \(!go\) return[\s\S]{0,120}dryRun: true/.test(body), true);
  chk('go 는 1 이어야 한다', /String\(p\.go \|\| ''\) === '1'/.test(GAS), true);
  /* 위에서부터 지우면 남은 행 번호가 밀려 엉뚱한 줄이 지워진다. */
  chk('아래에서부터 지운다', /kill\.sort\(function \(a, b\) \{ return b - a; \}\)/.test(body), true);
  /* 지우고 나면 모집단이 달라진다. 안 다시 세면 시트에 옛 등수가 남아
     성적표 문자로 그대로 나간다. */
  chk('지운 뒤 다시 센다', /recomputeExam\(t, cfg\.base, cfg\.qCount\)/.test(body), true);
  chk('기준 코호트가 없으면 안 건드린다', /if \(!cfg\) continue;/.test(body), true);
  /* 통째로 비우는 길은 없어야 한다. */
  chk('시트를 비우는 길은 없다', /clearContents|deleteRows\(2,/.test(body), false);
}

console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
process.exit(fail ? 1 : 0);
