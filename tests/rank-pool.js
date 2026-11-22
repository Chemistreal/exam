/* ============================================================
   석차 모집단 합산 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   새로 들인 회차(화학1 1-3단원 총괄평가 심화반, kch1to3-s)는 응시자가 적다.
   선생님 결정(2026-11-22): 그 석차·백분위는 **같은 범위 시험**
   (1-3단원 모의고사 kch1to3 · 그 동형 kch1to3-b) 응시자와 합산해서 매긴다.

   정본은 exams.json 의 `rankWith` 한 곳이다. 거기서
     · 엑셀 기록(기준 기록)  → cohort/baseline.json `from:"pool"` (tools/gen_pool_cohort.py)
     · 시트 줄(앱 채점)      → EXAM_COHORT[제목].pool 을 보고 앱스크립트가 센다
   로 갈라진다. 셋이 같은 말을 하는지 여기서 본다.

   여기서 지키는 것:
   - 합친 기준 기록 = 합친 회차들의 기준 기록의 합 (문항별 통계는 안 합친다)
   - .gs 의 EXAM_COHORT 도 같은 기준 기록과 같은 합산 회차 제목을 갖는다
   - 시트 재계산이 합친 회차의 줄까지 세어 석차·인원·문자를 맞춘다
   - 두 회차를 다 본 학생은 **한 번만** 센다(이 회차 점수로)
   - 합친 회차(kch1to3) 쪽 석차는 **안 바뀐다** — 합산은 한 방향이다
   - `?action=cohort` 가 재계산과 같은 인원을 말한다(화면 석차 = 문자 석차)
   - 밤마다 도는 기준 기록 갱신이 합친 기록을 시트만으로 덮지 않는다
   - 성적표가 «이 회차 응시 기록 861명» 이 아니라 합산이라고 말한다

   실행:  node tests/rank-pool.js
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
const HTML = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const exams = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
const baseline = JSON.parse(fs.readFileSync(path.join(ROOT, 'cohort', 'baseline.json'), 'utf8')).exams;

const ID = 'kch1to3-s';
const EXAM = exams.find(e => e.id === ID);
const MEMBERS = (EXAM && EXAM.rankWith) || [];
const titleOf = id => exams.find(e => e.id === id).title;
const T_S = titleOf(ID), T_A = titleOf('kch1to3'), T_B = titleOf('kch1to3-b');
const spread = h => { const o = []; Object.keys(h).sort((a, b) => a - b)
  .forEach(k => { for (let i = 0; i < h[k]; i++) o.push(Number(k)); }); return o; };

console.log('── 정본과 기준 기록 ──');
chk('합칠 회차가 적혀 있다', MEMBERS, ['kch1to3', 'kch1to3-b']);
const pool = baseline[ID] || {};
chk('합친 기준 기록이 있다', pool.from, 'pool');
chk('어느 회차를 합쳤는지 적혀 있다', pool.pool, MEMBERS);
const sum = {};
MEMBERS.forEach(m => Object.entries(baseline[m].hist).forEach(([k, v]) => { sum[k] = (sum[k] || 0) + v; }));
chk('합친 분포 = 두 회차 분포의 합', spread(pool.hist || {}), spread(sum));
chk('인원 = 두 회차 인원의 합', pool.n, MEMBERS.reduce((a, m) => a + baseline[m].n, 0));
chk('문항별 통계는 안 합친다(문항이 다르다)', [!!pool.qc, !!pool.q], [false, false]);
const BASE_POOL = spread(pool.hist || {});
const BASE_A = spread(baseline.kch1to3.hist);

/* ── 시트 흉내 (tests/rank-recompute.js 와 같은 모양) ── */
function fakeSheet(rows) {
  const grid = rows.map(r => r.slice());
  return {
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
}
function load(sheet) {
  const other = {};
  const gas = {
    Logger: { log() {} },
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ({
        getSheetByName: n => (n === '성적기록' ? sheet : (other[n] || null)),
        insertSheet: n => (other[n] = fakeSheet([])),
      }),
      flush() {},
    },
    LockService: { getScriptLock: () => ({ waitLock() {}, tryLock() { return true; }, releaseLock() {} }) },
    ContentService: {
      MimeType: { JSON: 'json', JAVASCRIPT: 'js' },
      createTextOutput: t => ({ _t: t, setMimeType() { return this; }, getContent() { return t; } }),
    },
    Utilities: { formatDate: GAS_ENV.formatDate },
    Session: { getScriptTimeZone: () => 'Asia/Seoul' },
    PropertiesService: { getScriptProperties: () => ({ getProperty: () => '' }) },
    ScriptApp: { getProjectTriggers: () => [] },
    /* Date 만 바깥 것을 준다 — 시트 칸의 날짜가 `instanceof Date` 로 읽혀야 한다.
       Array 를 바깥 것으로 덮으면 .gs 의 배열 글자(['제목'])가 `instanceof Array`
       에 안 걸려 EXAM_TITLES 를 한 겹 더 싸 버린다(창구가 0명을 말한다). */
    Date: Date,
  };
  vm.createContext(gas);
  vm.runInContext(SRC, gas);
  gas.fillReportMessages = () => {};
  return gas;
}
/* 열: [0시험 1이름 2링크 3저장시각 … 6학교 7학년 8원점수(=맞은 수) 9만점 … 13전체누적인원 14맞은개수 16답안 17문자] */
function row(exam, name, school, correct, day, ans) {
  const r = new Array(18).fill('');
  r[0] = exam; r[1] = name; r[3] = new Date(Date.now() - (30 - (day || 0)) * 86400000);
  r[6] = school; r[7] = '2'; r[8] = correct; r[9] = 60;
  r[10] = Math.round(correct / 60 * 1000) / 10; r[11] = 0; r[12] = 1; r[13] = 1; r[14] = correct;
  r[16] = "'" + (ans || String((correct % 4) + 1).repeat(60));
  return r;
}

console.log('\n── .gs 의 표 ──');
{
  const gas = load(fakeSheet([]));
  const c = gas.EXAM_COHORT[T_S] || {};
  chk('총괄평가 제목에 합친 기준 기록이 실렸다', (c.base || []).slice().sort((a, b) => a - b), BASE_POOL);
  chk('합칠 회차 제목이 실렸다', c.pool, [T_A, T_B]);
  chk('1-3단원 모의고사 쪽은 합치지 않는다(한 방향)', (gas.EXAM_COHORT[T_A] || {}).pool, undefined);
  chk('밤마다 도는 갱신이 합친 기록을 안 덮는다',
      gas._baselineKeepWhy_({ from: 'pool', n: 861, hist: {} }, 900, false), '합산모집단');
}

console.log('\n── 시트 재계산 ──');
/* 총괄평가: 가(40)·나(30)   모의고사: 다(50)·라(20)   동형: 마(45)·가(10, 예전에 본 것)
   → 총괄평가 모집단 = 기준 861 + 가·나 + 다·라·마 (가는 한 번만) */
const rows = [
  row(T_S, '가학생', 'A중', 40, 10),
  row(T_S, '나학생', 'A중', 30, 11),
  row(T_A, '다학생', 'B중', 50, 1),
  row(T_A, '라학생', 'B중', 20, 2),
  row(T_B, '마학생', 'C중', 45, 3),
  row(T_B, '가학생', 'A중', 10, 0),
];
{
  const sh = fakeSheet(rows);
  const gas = load(sh);
  gas.recomputeAllExams();
  const S = sh._grid.filter(r => r[0] === T_S), A = sh._grid.filter(r => r[0] === T_A);
  const N = BASE_POOL.length + 2 + 3;
  chk('총괄평가 인원 = 합친 기준 + 두 회차 시트 학생(같은 학생은 한 번)', S.map(r => r[13]), [N, N]);
  const others = [40, 30, 50, 20, 45];
  const rank = t => BASE_POOL.filter(v => v > t).length + others.filter(v => v > t).length + 1;
  chk('가학생 석차는 합친 모집단 안에서', S.find(r => r[1] === '가학생')[12], rank(40));
  chk('나학생 석차', S.find(r => r[1] === '나학생')[12], rank(30));
  chk('문자도 합친 인원을 말한다',
      S.every(r => String(r[17]).indexOf('석차 ' + r[12] + '/' + N) > 0), true);
  const NA = BASE_A.length + 2;
  chk('1-3단원 모의고사 쪽 인원은 그대로(총괄평가 학생을 안 넣는다)', A.map(r => r[13]), [NA, NA]);
  chk('동형 쪽 줄의 시험명은 안 바뀐다', sh._grid.filter(r => r[0] === T_B).length, 2);
}

console.log('\n── 화면이 묻는 창구(?action=cohort) ──');
{
  const gas = load(fakeSheet(rows));
  const ask = id => JSON.parse(String(gas.doGet({ parameter: { action: 'cohort', exam: id, callback: '__c' } })._t)
    .replace(/^__c\(/, '').replace(/\)$/, ''));
  const s = ask(ID);
  chk('총괄평가: 시트 학생 5명(가는 한 번)', s.n, 5);
  chk('그중 합친 회차에서 온 사람', s.pooled, 3);
  chk('분포에 이 회차 점수(40)가 들어가고 예전 점수(10)는 안 들어간다', [s.hist['40'], s.hist['10']], [1, undefined]);
  const a = ask('kch1to3');
  chk('1-3단원 모의고사는 자기 줄만', [a.n, a.pooled], [2, undefined]);
}

console.log('\n── 성적표 문구 ──');
{
  chk('합친 모집단이면 합산이라고 말한다', /같은 범위 시험\(\$\{esc\(rp\.pooled\.join/.test(HTML), true);
  chk('Word 에도 같은 말을 한다', /석차·백분위는 같은 범위 시험\('\+_rp\.pooled\.join/.test(HTML), true);
  /* final.html 의 poolTitles 를 그대로 떼어 와 돌린다 */
  const a = HTML.indexOf('function poolTitles(exam){');
  const b = HTML.indexOf('\n}', a) + 2;
  const f = new Function('BASELINE', 'FINAL_EXAMS', 'cohortKey', HTML.slice(a, b) + '\nreturn poolTitles;');
  const pt = f(baseline, exams, id => id);
  chk('합친 회차 이름을 돌려준다', pt(EXAM), [T_A, T_B]);
  chk('합치지 않은 회차는 null', pt(exams.find(e => e.id === 'kch1to3')), null);
}

console.log(fail ? `\n${fail}개 실패` : '\n결과: 전부 통과');
process.exit(fail ? 1 : 0);
