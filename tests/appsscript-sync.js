/* ============================================================
   시트 동기화(doGet) 회귀 테스트 — 순수 node
   ------------------------------------------------------------
   시트는 시험을 **제목 문자열**로 구분한다. 저장(doPost)은 `d.exam = cur.title`
   로 제목을 쓰고, 불러오기(doGet)는 시험 id 를 받아 EXAM_TITLES 로 제목을 찾아
   그 행만 거른다.

   그 표에 시험이 빠져 있으면 `want` 가 null 이 되어 **모든 시험의 행을 그대로
   돌려준다.** 실제로 이 표에는 옛 kch* 9개만 있었고 지금 쓰는 38개는 하나도
   없었다. 그 상태로 동기화를 붙였다면 다른 시험 응시 기록이 통계 풀에 섞여
   또래 정답률과 백분위가 조용히 틀어졌을 것이다.

   여기서 지키는 것:
   - final.html 의 모든 시험이 EXAM_TITLES 에 있다
   - 제목을 바꾸기 전에 쌓인 행('화올 2018')도 계속 걸린다
   - 없앤 id 로 물어봐도 남긴 시험의 행이 나온다(COHORT_ALIAS 와 같은 취지)
   - 다른 시험의 행은 절대 섞이지 않는다

   실행:  node tests/appsscript-sync.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const gs = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
const html = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');

let pass = 0, fail = 0;
function chk(desc, got, exp) {
  const ok = JSON.stringify(got) === JSON.stringify(exp);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc +
    (ok ? '' : ' → ' + JSON.stringify(got) + ' (기대 ' + JSON.stringify(exp) + ')'));
  ok ? pass++ : fail++;
}

/* .gs 에서 표를 그대로 떼어 온다(구현과 테스트가 갈라지지 않게) */
const block = gs.slice(gs.indexOf('var EXAM_TITLES = {'),
                       gs.indexOf('\n};', gs.indexOf('var EXAM_TITLES = {')) + 3);
const EXAM_TITLES = new Function(block + '; return EXAM_TITLES;')();
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
const COHORT_ALIAS = JSON.parse(
  html.split('const COHORT_ALIAS=')[1].split('};')[0].replace(/'/g, '"') + '}');

/* ── 1. 모든 시험이 표에 있고, 제목이 지금 것과 맞는가 ── */
{
  const missing = EXAMS.filter(e => !EXAM_TITLES[e.id]).map(e => e.id);
  chk('표에 빠진 시험 없음', missing, []);
  const wrong = EXAMS.filter(e => {
    const t = EXAM_TITLES[e.id];
    return !(Array.isArray(t) ? t : [t]).includes(e.title);
  }).map(e => e.id + ' → ' + e.title);
  chk('지금 제목이 모두 표에 들어 있음', wrong, []);
}

/* ── 2. 없앤 id 로 물어봐도 남긴 시험과 같은 제목 묶음이 나온다 ── */
{
  Object.keys(COHORT_ALIAS).forEach(gone => {
    const kept = COHORT_ALIAS[gone];
    chk(gone + ' 로 물어도 ' + kept + ' 와 같은 제목 묶음',
      EXAM_TITLES[gone], EXAM_TITLES[kept]);
  });
}

/* ── 3. doGet 의 거르기가 실제로 맞게 도는가 ──
   가짜 시트를 만들어 걸러 본다. 여기가 틀리면 통계 풀에 남의 기록이 섞인다. */
{
  // doGet 안의 거르기 규칙을 그대로 옮긴 것 (.gs 를 고치면 여기도 같이 고친다)
  function filterRows(examId, rows) {
    let want = EXAM_TITLES[examId] || null;
    if (want && !(want instanceof Array)) want = [want];
    return rows.filter(r => !(want && want.indexOf(String(r[0])) < 0));
  }
  const rows = [
    ['KMChC 2018', '가'],            // 지금 제목
    ['화올 2018', '나'],              // 이름 바꾸기 전에 쌓인 행
    ['KMChC 2018 · 동형 2세트', '다'], // 잠깐 썼던 제목
    ['KMChC 2019', '라'],            // 다른 시험
    ['JMChC 모의고사 1회', '마'],      // 또 다른 시험
  ];
  chk('hwol-2018 로 거르면 세 이름 모두 걸린다',
    filterRows('hwol-2018', rows).map(r => r[1]), ['가', '나', '다']);
  chk('없앤 kmchc-2018 로 걸러도 같은 결과',
    filterRows('kmchc-2018', rows).map(r => r[1]), ['가', '나', '다']);
  chk('hwol-2019 에는 2018 행이 섞이지 않는다',
    filterRows('hwol-2019', rows).map(r => r[1]), ['라']);
  chk('jmchc-1 에는 KMChC 행이 섞이지 않는다',
    filterRows('jmchc-1', rows).map(r => r[1]), ['마']);
  chk('표에 없는 id 는 거르지 않는다(하위호환)',
    filterRows('없는시험', rows).length, rows.length);
}

/* ── 4. index.html 의 옛 시험도 표에 남아 있어야 한다 ──
   index.html 은 final.html 과 **같은 시트 엔드포인트**를 쓴다. 표에서 빠지면
   그 요청의 필터가 통째로 꺼져(want=null) 모든 시험의 행이 딸려 간다 —
   옛 시험 통계에 KMChC 응시 기록이 섞인다. 실제로 한 번 지웠다가 되살렸다. */
{
  const legacy = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const ids = [...new Set([...legacy.matchAll(/id:"([\w-]+)",title:"([^"]+)"/g)]
    .map(m => [m[1], m[2]]).map(JSON.stringify))].map(JSON.parse);
  chk('index.html 에서 시험을 찾았다', ids.length > 0, true);
  const missing = ids.filter(([id]) => !EXAM_TITLES[id]).map(([id]) => id);
  chk('옛 시험이 표에 모두 있다', missing, []);
  const wrongTitle = ids.filter(([id, t]) => {
    const v = EXAM_TITLES[id];
    return !(Array.isArray(v) ? v : [v]).includes(t);
  }).map(([id, t]) => id + ' → ' + t);
  chk('옛 시험 제목도 그대로 맞다', wrongTitle, []);
}

/* ── 5. 열쇠는 코드에 적혀 있으면 안 된다 ──
   이 파일은 공개 저장소에 올라가고 머지되면 자동 배포된다. */
{
  const hardcoded = /var\s+SECRET\s*=\s*['"][^'"]+['"]/.test(gs);
  chk('SECRET 이 코드에 하드코딩돼 있지 않음', hardcoded, false);
  chk('스크립트 속성에서 열쇠를 읽는다',
    /getScriptProperties\(\)\.getProperty\(\s*'SECRET'\s*\)/.test(gs), true);
  chk('열쇠가 없으면 응답에 경고를 싣는다', /payload\.warning\s*=/.test(gs), true);
}

console.log('\n결과: ' + pass + ' pass / ' + fail + ' fail');
process.exit(fail ? 1 : 0);
