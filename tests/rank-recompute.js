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
  const sheet = {
    _grid: grid,
    getLastRow: () => grid.length + 1,
    getRange(row, col, nRow, nCol) {
      nRow = nRow || 1; nCol = nCol || 1;
      const range = {
        getValue: () => (grid[row - 2] || [])[col - 1],
        getValues: () => { const out = [];
          for (let i = 0; i < nRow; i++) { const src = grid[row - 2 + i] || [], line = [];
            for (let j = 0; j < nCol; j++) line.push(src[col - 1 + j]);
            out.push(line); }
          return out; },
        setValues(vals) { for (let i = 0; i < vals.length; i++) {
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
    Utilities: {}, Session: { getScriptTimeZone: () => 'Asia/Seoul' },
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
        10백점환산 11백분위 12석차 13전체누적인원 14맞은개수 15영역별 16답안 17문자] */
function row(exam, name, school, correct, opts) {
  opts = opts || {};
  const r = new Array(18).fill('');
  r[0] = exam; r[1] = name; r[3] = new Date(2026, 0, 1 + (opts.day || 0));
  r[6] = school; r[7] = opts.grade || '2';
  r[8] = correct * 3; r[9] = (opts.nQ || 60) * 3;
  r[10] = Math.round(correct / (opts.nQ || 60) * 1000) / 10;
  r[11] = opts.pct != null ? opts.pct : 0;
  r[12] = opts.rank != null ? opts.rank : 1;   // 저장 순간에 박힌 옛 값
  r[13] = opts.n != null ? opts.n : 1;
  r[14] = correct;
  r[16] = "'" + String(opts.ans || String((correct % 4) + 1).repeat(opts.nQ || 60));
  return r;
}

const T6 = 'JMChC 모의고사 6회';
const BASE6 = (function () {           // 기준 기록 11명을 원점수로
  const out = [];
  Object.keys(baseline['jmchc-6'].hist).sort((a, b) => a - b).forEach(k => {
    for (let i = 0; i < baseline['jmchc-6'].hist[k]; i++) out.push(Number(k) * 3);
  });
  return out;
}());

function post(gas, d) {
  return JSON.parse(gas.doPost({ postData: { contents: JSON.stringify(d) } })._t);
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
  post(gas, { exam: T6, name: '다학생', school: 'A중', grade: '2', total: 60,
              max: 180, pct100: 33.3, percentile: 0, rank: 1, n: 1,
              correct: 20, areas: '', answers: '4'.repeat(60) });

  const n = BASE6.length + 3;                    // 기준 11명 + 학생 3명
  chk('모든 행이 같은 인원을 말한다', sh._grid.map(r => r[13]), [n, n, n]);
  chk('먼저 저장된 학생의 인원도 늘었다', of(sh, '가학생')[0][13], n);

  // 석차 = 나보다 높은 사람 수 + 1
  const higher = t => BASE6.filter(v => v > t).length
    + [120, 90, 60].filter(v => v > t).length;
  chk('가학생 석차', of(sh, '가학생')[0][12], higher(120) + 1);
  chk('나학생 석차', of(sh, '나학생')[0][12], higher(90) + 1);
  chk('다학생 석차', of(sh, '다학생')[0][12], higher(60) + 1);

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
{
  const gas = load(fakeSheet([]));
  const missing = exams.filter(e => !gas.EXAM_COHORT[e.title]).map(e => e.id);
  chk('모든 시험 제목에 설정이 있다', missing, []);

  const badQ = exams.filter(e => gas.EXAM_COHORT[e.title].q !== e.nQ).map(e => e.id);
  chk('문항 수가 맞다', badQ, []);
  chk('50문항 회차도 잡힌다',
      gas._recomputeConfigFor('KMChC 2026 제1차 · 일반').qCount, 50);

  // 옛 제목으로 쌓인 행도 재계산 대상이어야 한다.
  chk('옛 제목에도 설정이 있다', !!gas._recomputeConfigFor('화올 2018'), true);
  chk('표에 없는 제목은 건너뛴다', gas._recomputeConfigFor('있지도 않은 시험'), null);

  // 기준 기록이 화면(cohort/baseline.json)과 같아야 한다. 어긋나면 성적표와
  // 문자가 서로 다른 석차를 말한다.
  const drift = [];
  exams.forEach(e => {
    const want = [];
    const hist = (baseline[e.id] || {}).hist || {};
    Object.keys(hist).sort((a, b) => a - b).forEach(k => {
      for (let i = 0; i < hist[k]; i++) want.push(Number(k) * 3);
    });
    const got = gas.EXAM_COHORT[e.title].base.slice().sort((a, b) => a - b);
    if (JSON.stringify(got) !== JSON.stringify(want.sort((a, b) => a - b))) drift.push(e.id);
  });
  chk('기준 기록이 화면과 같다(원점수 = 맞은 수 × 3)', drift, []);

  const withBase = exams.filter(e => gas.EXAM_COHORT[e.title].base.length).length;
  chk('기준 기록이 실린 회차 수', withBase, Object.keys(baseline).length);
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

console.log('\n── 표를 손으로 고치지 않았다 ──');
{
  // EXAM_COHORT 는 tools/gen_gas_cohort.py 가 만든다. 손으로 고치면
  // 다음 생성 때 조용히 되돌아가므로 CI 가 어긋남을 잡아야 한다.
  chk('생성기가 있다', fs.existsSync(path.join(ROOT, 'tools', 'gen_gas_cohort.py')), true);
  chk('생성기가 만든 표라고 적혀 있다', /gen_gas_cohort\.py/.test(SRC), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
