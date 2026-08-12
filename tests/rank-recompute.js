/* ============================================================
   시트 석차 재계산 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   시트의 백분위·석차·전체누적인원은 **저장하는 그 순간**의 인원으로 한 번
   계산되어 행에 박제된다. 그래서 먼저 채점한 학생은 43명 중 몇 등, 나중
   학생은 44명 중 몇 등으로 남았다 — 그 숫자 그대로 성적표 문자가 나갔다.

   고치는 장치(recomputeExam)는 있었는데 `_recomputeConfigFor` 가
   '조준모의고사 0회' 에만 설정을 돌려주고 나머지는 null 이었다. 즉 실제로
   쓰는 회차는 재계산이 **한 번도 돌지 않았다**. EXAM_COHORT 가 그 빈자리다.

   여기서 지키는 것:
   - 한 명 더 채점하면 이미 저장된 학생의 인원·석차도 같이 늘어난다
   - 한 회차의 모든 행이 **같은 인원**을 말한다(43명/44명이 섞이지 않는다)
   - 성적표 문자의 '석차 x/n' 이 셀 값과 같다
   - 기준 코호트(cohort/baseline.json)가 화면과 시트에서 같다 — ×3(원점수)
   - 문항 수가 회차마다 반영된다(50문항 회차 6개)
   - 동명이인(이름 같고 학교 다름)은 두 사람으로 센다
   - EXAM_COHORT 가 시험 목록과 어긋나지 않는다(제목이 하나라도 빠지면 그
     회차는 재계산이 통째로 건너뛴다)
   - recomputeAllExams 는 제출이 없는 회차의 옛 행까지 훑는다

   실행:  node tests/rank-recompute.js
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

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
const exams = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
const baseline = JSON.parse(fs.readFileSync(path.join(ROOT, 'cohort', 'baseline.json'), 'utf8')).exams;

/* 시트 흉내. 행 번호는 1부터, 데이터는 2행부터 — 진짜와 같게 맞춰야
   삭제 순서나 열 어긋남 같은 실수가 여기서 걸린다. */
function fakeSheet(rows) {
  const grid = rows.map(r => r.slice());
  const io = { reads: 0, writes: 0 };   // 회차마다 시트를 다시 읽고 쓰면 저장이 느려진다
  const sheet = {
    _grid: grid,
    _io: io,
    getLastRow: () => grid.length + 1,
    getRange(row, col, nRow, nCol) {
      nRow = nRow || 1; nCol = nCol || 1;
      const range = {
        getValue: () => (grid[row - 2] || [])[col - 1],
        getValues: () => { if (nRow > 1 || nCol > 1) io.reads++; const out = [];
          for (let i = 0; i < nRow; i++) { const src = grid[row - 2 + i] || [], line = [];
            for (let j = 0; j < nCol; j++) line.push(src[col - 1 + j]);
            out.push(line); }
          return out; },
        setValues(vals) { io.writes++; for (let i = 0; i < vals.length; i++) {
          if (!grid[row - 2 + i]) grid[row - 2 + i] = [];
          for (let j = 0; j < vals[i].length; j++) grid[row - 2 + i][col - 1 + j] = vals[i][j]; }
          return range; },
        setValue(v) { if (!grid[row - 2]) grid[row - 2] = []; grid[row - 2][col - 1] = v; return range; },
        setFontWeight() { return range; },
      };
      return range;
    },
    appendRow(r) { grid.push(r.slice()); },
    deleteRow(r) { grid.splice(r - 2, 1); },
    setFrozenRows() {},
  };
  return sheet;
}

function load(sheet) {
  const gas = {
    Logger: { log() {} },
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ({ getSheetByName: () => sheet, insertSheet: () => sheet }),
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
    Date: Date, Math: Math, JSON: JSON, String: String, Number: Number,
    Object: Object, Array: Array, RegExp: RegExp,
  };
  vm.createContext(gas);
  vm.runInContext(SRC, gas);
  // 성적문자 탭 재생성은 시트 전체를 다시 쓰는 별개의 동작이라 여기선 끈다.
  gas.fillReportMessages = () => {};
  return gas;
}

/* 열: [0시험 1이름 2링크 3저장시각 4수험번호 5응시일 6학교 7학년 8원점수 9만점
        10백점환산 11백분위 12석차 13전체누적인원 14맞은개수 15영역별 16답안 17문자]

   [주의] 8열 이름은 '원점수' 지만 final.html 이 보내는 값은 `total: correct`,
   즉 **맞은 문항 수**다(9열 '만점' 도 180이 아니라 문항 수). 이 하네스가
   예전에 correct*3 을 넣는 바람에, 기준 기록이 3배로 들어간 진짜 버그를
   테스트가 통과시켜 줬다 — 화면은 3/15, 문자는 12/15 였다.
   아래 payloadRow() 는 앱이 보내는 형태를 그대로 쓴다. */
function row(exam, name, school, correct, opts) {
  opts = opts || {};
  const r = new Array(18).fill('');
  r[0] = exam; r[1] = name; r[3] = new Date(2026, 0, 1 + (opts.day || 0));
  r[6] = school; r[7] = opts.grade || '2';
  r[8] = correct; r[9] = (opts.nQ || 60);
  r[10] = Math.round(correct / (opts.nQ || 60) * 1000) / 10;
  r[11] = opts.pct != null ? opts.pct : 0;
  r[12] = opts.rank != null ? opts.rank : 1;   // 저장 순간에 박힌 옛 값
  r[13] = opts.n != null ? opts.n : 1;
  r[14] = correct;
  r[16] = "'" + String(opts.ans || String((correct % 4) + 1).repeat(opts.nQ || 60));
  return r;
}

const T6 = 'JMChC 모의고사 6회';
const BASE6 = (function () {           // 기준 기록 11명 · 단위는 맞은 문항 수
  const out = [];
  Object.keys(baseline['jmchc-6'].hist).sort((a, b) => a - b).forEach(k => {
    for (let i = 0; i < baseline['jmchc-6'].hist[k]; i++) out.push(Number(k));
  });
  return out;
}());

function post(gas, d) {
  return JSON.parse(gas.doPost({ postData: { contents: JSON.stringify(d) } })._t);
}
/* final.html 의 saveToSheetFinal 이 실제로 보내는 형태.
   total = 맞은 문항 수 · max = 문항 수. 여기서 단위를 지어내면 안 된다. */
function appPayload(exam, name, school, correct, nQ, answers) {
  nQ = nQ || 60;
  return { exam: exam, name: name, school: school, grade: '2',
           total: correct, max: nQ, pct100: Math.round(correct / nQ * 1000) / 10,
           percentile: 0, rank: '1/1', n: 1, correct: correct, areas: '',
           answers: answers || String((correct % 4) + 1).repeat(nQ) };
}
const of = (sh, name) => sh._grid.filter(r => String(r[1]) === name);

console.log('── 나중에 채점한 학생이 앞사람의 인원을 늘린다 ──');
{
  // 두 학생이 각각 "그 순간의 인원"으로 굳은 채 저장돼 있다 — 11명, 12명.
  const sh = fakeSheet([
    row(T6, '가학생', 'A중', 40, { day: 0, rank: 3, n: 11 }),
    row(T6, '나학생', 'A중', 30, { day: 1, rank: 9, n: 12 }),
  ]);
  const gas = load(sh);
  chk('시작은 인원이 제각각', sh._grid.map(r => r[13]), [11, 12]);

  // 세 번째 학생을 채점해 저장한다.
  post(gas, appPayload(T6, '다학생', 'A중', 20, 60, '4'.repeat(60)));

  const n = BASE6.length + 3;                    // 기준 11명 + 학생 3명
  chk('모든 행이 같은 인원을 말한다', sh._grid.map(r => r[13]), [n, n, n]);
  chk('먼저 저장된 학생의 인원도 늘었다', of(sh, '가학생')[0][13], n);

  // 석차 = 나보다 높은 사람 수 + 1
  const higher = t => BASE6.filter(v => v > t).length
    + [40, 30, 20].filter(v => v > t).length;
  chk('가학생 석차', of(sh, '가학생')[0][12], higher(40) + 1);
  chk('나학생 석차', of(sh, '나학생')[0][12], higher(30) + 1);
  chk('다학생 석차', of(sh, '다학생')[0][12], higher(20) + 1);

  // 문자도 같은 숫자를 말해야 한다 — 셀만 고치고 문자를 두면 학부모는 옛 숫자를 본다.
  const msgs = sh._grid.map(r => String(r[17]));
  chk('문자가 모두 새 인원을 말한다', msgs.every(m => m.indexOf('/' + n + '\n') > 0), true);
  chk('문자의 석차가 셀과 같다',
      sh._grid.every(r => String(r[17]).indexOf('석차 ' + r[12] + '/' + r[13]) > 0), true);
  chk('문자에 옛 인원이 남지 않았다', msgs.some(m => /석차 \d+\/(11|12)\b/.test(m)), false);
}

console.log('\n── 동명이인은 두 사람 ──');
{
  const sh = fakeSheet([
    row(T6, '김민준', 'A중', 40, { day: 0 }),
    row(T6, '김민준', 'B중', 20, { day: 1, ans: '2'.repeat(60) }),
  ]);
  const gas = load(sh);
  gas.recomputeExam(T6, BASE6, 60);
  chk('학교가 다르면 따로 센다', sh._grid[0][13], BASE6.length + 2);
  chk('두 줄 다 남는다', sh._grid.length, 2);
}
{
  // 같은 사람이 두 번 채점되면(답안이 달라 중복 삭제엔 안 걸린다) 한 명으로 센다.
  const sh = fakeSheet([
    row(T6, '김민준', 'A중', 40, { day: 0 }),
    row(T6, '김민준', 'A중', 44, { day: 1, ans: '2'.repeat(60) }),
  ]);
  const gas = load(sh);
  gas.recomputeExam(T6, BASE6, 60);
  chk('같은 학생은 한 명으로 센다', sh._grid[0][13], BASE6.length + 1);
}

console.log('\n── 회차마다 설정이 붙어 있다 ──');

/* ── 50문항 회차를 골라 쓴다 ────────────────────────────────────────
   여기에 회차 제목을 박아 두었더니 그 회차를 지우는 날 검사가 깨졌다
   (2026-08-08, KMChC 일반과정 세 회차를 지웠을 때). 검사가 재는 것은
   "문항 수가 60으로 박히지 않는가" 이지 특정 회차가 아니다. 목록에서
   50문항짜리를 하나 골라 쓴다 — 지워도 다른 것이 대신 선다. */
const EX50 = (() => {
  const all = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'exams.json'), 'utf8'));
  const e = all.find(x => x.nQ === 50);
  if (!e) { console.log('실패: 50문항 회차가 하나도 없다 — 이 검사가 잴 것이 없어졌다'); process.exit(1); }
  return e;
})();

{
  const gas = load(fakeSheet([]));
  const missing = exams.filter(e => !gas.EXAM_COHORT[e.title]).map(e => e.id);
  chk('모든 시험 제목에 설정이 있다', missing, []);

  const badQ = exams.filter(e => gas.EXAM_COHORT[e.title].q !== e.nQ).map(e => e.id);
  chk('문항 수가 맞다', badQ, []);
  chk('50문항 회차도 잡힌다',
      gas._recomputeConfigFor(EX50.title).qCount, 50);

  // 옛 제목으로 쌓인 행도 재계산 대상이어야 한다.
  chk('옛 제목에도 설정이 있다', !!gas._recomputeConfigFor('화올 2018'), true);
  chk('표에 없는 제목은 건너뛴다', gas._recomputeConfigFor('있지도 않은 시험'), null);

  /* 기준 기록의 **단위**가 앱이 보내는 값과 같아야 한다.
     시트 8열 이름은 '원점수' 지만 final.html 은 `total: correct`, 즉 맞은 문항
     수를 보낸다. 여기에 3을 곱해 넣었던 적이 있는데, 학생이 전원 꼴찌가 되어
     화면은 3/15, 문자는 12/15 라고 말했다. 곱셈이 조용히 섞이면 안 된다. */
  const drift = [];
  exams.forEach(e => {
    const want = [];
    const hist = (baseline[e.id] || {}).hist || {};
    Object.keys(hist).sort((a, b) => a - b).forEach(k => {
      for (let i = 0; i < hist[k]; i++) want.push(Number(k));
    });
    const got = gas.EXAM_COHORT[e.title].base.slice().sort((a, b) => a - b);
    if (JSON.stringify(got) !== JSON.stringify(want.sort((a, b) => a - b))) drift.push(e.id);
  });
  chk('기준 기록이 화면과 같은 단위다(맞은 문항 수)', drift, []);
  // 맞은 문항 수는 문항 수를 넘을 수 없다. 곱셈이 섞이면 여기서 걸린다.
  const over = exams.filter(e => gas.EXAM_COHORT[e.title].base.some(v => v > e.nQ)).map(e => e.id);
  chk('기준 점수가 문항 수를 넘지 않는다', over, []);

  /* ⚠ 기준 기록에는 **exams.json 에 없는 회차**가 섞일 수 있다(자동 갱신이
     엑셀에서 통째로 긁어 온다). 그것을 .gs 표가 안 실은 것은 표의 잘못이
     아니다 — 앱이 모르는 시험이라 실을 자리가 없다.
     그래서 견주는 대상은 **앱이 아는 회차** 로 좁히고, 남는 것은 따로 말한다.
     (2026-08 자동 갱신이 j0·kmchc-2018 을 들여왔는데 둘 다 시험 목록에 없다.) */
  const known = Object.keys(baseline).filter(id => exams.some(e => e.id === id));
  const orphan = Object.keys(baseline).filter(id => !exams.some(e => e.id === id));
  const withBase = exams.filter(e => gas.EXAM_COHORT[e.title].base.length).length;
  chk('앱이 아는 회차는 기준 기록이 다 실렸다', withBase, known.length);
  if (orphan.length) console.log('  ※ 시험 목록에 없는 기준 기록 ' + orphan.length + '개: ' + orphan.join(', '));
}

console.log('\n── 제출이 없는 회차도 훑는다 ──');
{
  // 옛날에 저장돼 인원이 굳은 회차는 새 제출이 없으면 영영 그대로다.
  // 매일 새벽 트리거가 recomputeAllExams 로 한 번 훑는다.
  const T14 = 'JMChC 모의고사 14회';
  const sh = fakeSheet([
    row(T6, '가학생', 'A중', 40, { day: 0, n: 11 }),
    row(T14, '라학생', 'C중', 30, { day: 0, n: 5 }),
    row('화학1 1단원 모의고사', '마학생', 'D중', 20, { day: 0, n: 3 }),   // 설정 없는 옛 시험
  ]);
  const gas = load(sh);
  gas.recomputeAllExams();
  chk('6회가 맞춰졌다', sh._grid[0][13], BASE6.length + 1);
  chk('14회도 맞춰졌다', sh._grid[1][13], baseline['jmchc-14'].n + 1);
  chk('설정 없는 옛 시험은 손대지 않는다', sh._grid[2][13], 3);
}

console.log('\n── 시트가 앱과 같은 석차를 말한다 ──');
{
  /* 이 검사가 없어서 단위가 3배 어긋난 채 배포됐다. 화면은 3/15, 문자는
     12/15 였고 두 숫자 모두 "정상으로 보이는" 값이라 아무도 못 알아챈다.
     앱이 쓰는 규칙(기준 기록 ∪ 이 브라우저 학생, rankIn)으로 직접 세어
     시트가 낸 값과 맞대 본다. */
  const nQ = 60, sh = fakeSheet([]), gas = load(sh);
  const students = [['가', 40], ['나', 13], ['다', 52], ['라', 25], ['마', 40]];
  students.forEach(([nm, c], i) =>
    post(gas, appPayload(T6, nm, 'A중', c, nQ, String((i % 4) + 1).repeat(nQ))));

  // 앱의 셈: 모집단 = 기준 기록 + 이 브라우저 학생 · 석차 = 나보다 높은 사람 + 1
  const pool = BASE6.concat(students.map(s => s[1]));
  const rankIn = my => pool.filter(t => t > my).length + 1;
  const pctOf = my => {
    const b = pool.filter(t => t < my).length, e = pool.filter(t => t === my).length;
    return Math.round((b + 0.5 * e) / pool.length * 1000) / 10;
  };
  const bad = [];
  students.forEach(([nm, c]) => {
    const r = of(sh, nm)[0];
    if (r[12] !== rankIn(c)) bad.push(`${nm} 석차 시트 ${r[12]} ≠ 앱 ${rankIn(c)}`);
    if (r[13] !== pool.length) bad.push(`${nm} 인원 시트 ${r[13]} ≠ 앱 ${pool.length}`);
    if (r[11] !== pctOf(c)) bad.push(`${nm} 백분위 시트 ${r[11]} ≠ 앱 ${pctOf(c)}`);
  });
  chk('석차·인원·백분위가 앱과 한 자리도 안 어긋난다', bad, []);
  // 동점자는 같은 석차여야 한다(가·마 둘 다 40)
  chk('동점은 같은 석차', of(sh, '가')[0][12], of(sh, '마')[0][12]);
  // 1등은 최고점, 꼴찌 석차는 인원을 넘지 않는다
  chk('최고점이 1등 근처다', of(sh, '다')[0][12] <= 2, true);
  chk('석차가 인원을 넘지 않는다', students.every(([nm]) => of(sh, nm)[0][12] <= pool.length), true);
}

console.log('\n── 저장하는 즉시 다른 회차까지 맞는다 ──');
{
  // 한 회차만 맞추면 다른 회차의 옛 행은 다음 제출까지 굳은 채 남는다.
  // 저장 한 번이 시트 전체를 맞춰야 하고, 그러면서 느려지면 안 된다.
  const T14 = 'JMChC 모의고사 14회';
  const sh = fakeSheet([
    row(T6, '가학생', 'A중', 40, { day: 0, n: 11 }),
    row(T14, '라학생', 'C중', 30, { day: 0, n: 5 }),
    row(T14, '마학생', 'C중', 20, { day: 1, n: 6, ans: '2'.repeat(60) }),
  ]);
  const gas = load(sh);
  sh._io.reads = 0; sh._io.writes = 0;

  // 6회 학생 한 명을 저장한다 — 14회는 건드리지도 않았다.
  post(gas, appPayload(T6, '나학생', 'A중', 30, 60, '3'.repeat(60)));

  chk('6회가 맞춰졌다', sh._grid.filter(r => r[0] === T6).map(r => r[13]),
      [BASE6.length + 2, BASE6.length + 2]);
  chk('손대지 않은 14회도 같이 맞춰졌다',
      sh._grid.filter(r => r[0] === T14).map(r => r[13]),
      [baseline['jmchc-14'].n + 2, baseline['jmchc-14'].n + 2]);
  /* 이 자가 지키는 것은 «읽기가 **회차 수만큼 늘지 않는다**» 이다.
     38개 회차를 각각 읽고 쓰면 저장 한 번이 몇십 초가 된다.

     두 번인 까닭(2026-08-12):
       ① 같은 응시가 이미 있나 찾는다 — 있으면 덧붙이지 않고 그 줄을 고친다.
          이것이 없으면 다시 보낼 때마다 새 줄이 생기고, 재계산이 «최신 1건만
          남김» 으로 정리하면서 7월 기록의 날짜가 오늘로 바뀐다
       ② 재계산이 시트를 통째로 읽는다
     둘 다 **회차 수와 무관한 한 번**이다. 늘어나는 것은 여기서 막는다. */
  chk('시트 읽기가 회차 수를 안 탄다 (저장 한 번에 두 번)', sh._io.reads, 2);
  chk('시트에 한 번만 쓴다', sh._io.writes, 1);
}

console.log('\n── 표를 손으로 고치지 않았다 ──');
{
  // EXAM_COHORT 는 tools/gen_gas_cohort.py 가 만든다. 손으로 고치면
  // 다음 생성 때 조용히 되돌아가므로 CI 가 어긋남을 잡아야 한다.
  chk('생성기가 있다', fs.existsSync(path.join(ROOT, 'tools', 'gen_gas_cohort.py')), true);
  chk('생성기가 만든 표라고 적혀 있다', /gen_gas_cohort\.py/.test(SRC), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
