/* ============================================================
   응시 이력은 브라우저가 아니라 학생에게 붙는다 — 회귀 테스트
   ------------------------------------------------------------
   성장 대시보드·성장 추적·숙달 추적은 **그 브라우저에 채점해 둔 기록**만
   세고 있었다. 아홉 군데가 각자 같은 규칙을 베껴 쓰면서.

   그래서 학부모 휴대폰에서 공유 링크를 열면, 그 폰이 우연히 열어 본 회차만
   잡혀 "지금까지 2회 응시" 라고 나왔다 — 실제로는 여섯 번을 봤는데.
   `#r=` 링크를 열면 그 브라우저에 기록이 하나 생기므로, 링크를 두 개 열어
   본 폰은 2회가 된다. 학부모가 보는 화면이 아이의 응시 이력을 **틀리게**
   말하고 있었다. 선생님이 학원 PC 를 바꿔도 같은 일이 난다.

   시트에는 어느 기기에서 채점했든 다 들어 있다. 학생 하나를 이름으로 물어
   전 회차를 받아 두고, 이 브라우저 기록과 합쳐 한 곳에서 낸다(histOf).

   여기서 지키는 것:
   - 시트 기록과 이 브라우저 기록을 합친다
   - 이름은 공백을 지우고 견준다('박바다' = '박 바다')
   - 한 회차에 여러 번이면 가장 최근 것 하나만
   - **회차 번호 순**으로 늘어놓는다(채점한 시각이 아니다)
   - '지난 진단' 은 지금 보고 있는 회차의 바로 앞 회차다
   - 문항 수가 안 맞는 기록은 넣지 않는다(다른 시험이다)
   - 시트 기록을 localStorage 에 쓰지 않는다(학부모 폰에 남길 이유가 없다)
   - 다시 그릴 때 저장·시트 전송을 되풀이하지 않는다
   - 아홉 군데가 모두 이 한 곳을 쓴다

   실행:  node tests/history.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};
function cut(src, name) {
  const at = src.search(new RegExp(`^(?:async )?function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`${name} 을 못 찾았다`);
  let d = 0;
  for (let j = src.indexOf('{', at); j < src.length; j++) {
    if (src[j] === '{') d++;
    else if (src[j] === '}') { d--; if (!d) return src.slice(at, j + 1); }
  }
  throw new Error(`${name} 의 끝을 못 찾았다`);
}

/* 시험 셋 · 저장소는 여기서 세운다. 채점 규칙(okq)·이력 규칙(histOf)은
   final.html 원본을 그대로 오려 쓴다 — 규칙이 바뀌면 여기서 걸린다. */
const ctx = { console, STORE: {}, FINAL_EXAMS: [] };
vm.createContext(ctx);
// accSet·allc·okq 는 const 화살표라 따로 오려 낸다
function cutConst(name) {
  const at = SRC.search(new RegExp(`^const ${name}=`, 'm'));
  const i = SRC.indexOf('{', at), eol = SRC.indexOf('\n', at);
  if (i < 0 || i > eol) return SRC.slice(at, eol);
  let d = 0;
  for (let j = i; j < SRC.length; j++) {
    if (SRC[j] === '{') d++;
    else if (SRC[j] === '}') { d--; if (!d) return SRC.slice(at, j + 1); }
  }
}
vm.runInContext([
  cutConst('accSet'), cutConst('allc'), cutConst('okq'),
  cut(SRC, 'examFamily'), cut(SRC, 'examOrder'), cut(SRC, 'cmpExam'),
  cut(SRC, 'shortExam'), cut(SRC, 'histAt'),
  'var _EXORD=null;',
  SRC.match(/^const COHORT_ALIAS=.*$/m)[0],
  SRC.match(/^const cohortKey=.*$/m)[0],
  SRC.match(/^const nameKey=.*$/m)[0],
  'var HIST_ROWS=null, HIST_FOR="", HIST_TRIED="";',
  'function subs(id){ return STORE[cohortKey(id)] || []; }',
  // 학생별 파이널(student-finals.json) — 이 판에는 없는 것으로 세운다.
  // histOf 가 회차를 examById 로 찾게 되면서(2026-08-21) 같이 오려 낸다.
  'var STUDENT_FINALS=[];',
  cut(SRC, 'examById'),
  cut(SRC, 'histOf'),
  'Object.assign(globalThis,{histOf, nameKey, cmpExam, shortExam, histAt, examFamily,'
  + ' setHist:function(r,f){HIST_ROWS=r;HIST_FOR=f;}, resetOrd:function(){_EXORD=null;}});',
].join('\n'), ctx);

/* 시험 둘: 60문항짜리와 50문항짜리 */
const E = [
  { id: 'a', title: 'A회', nQ: 3, key: [1, 2, 3] },
  { id: 'b', title: 'B회', nQ: 3, key: [1, 1, 1] },
  { id: 'c', title: 'C회', nQ: 2, key: [4, 4] },
];
const rec = (name, ans, ts, correct) =>
  ({ name, school: 'X중', grade: '2', ans, ts, correct, total: ans.length, wrong: ans.length - correct });

const reset = () => { ctx.FINAL_EXAMS = E; ctx.STORE = {}; ctx.setHist(null, ''); ctx.resetOrd(); };

console.log('── 이 브라우저 기록만 있을 때 ──');
{
  reset();
  ctx.STORE.a = [rec('박바다', [1, 2, 3], 100, 3)];
  ctx.STORE.b = [rec('박바다', [1, 1, 1], 200, 3)];
  const h = ctx.histOf('박바다');
  chk('두 회차', h.map(x => x.e.id), ['a', 'b']);
  chk('오래된 것이 먼저', h.map(x => x.ts), [100, 200]);
  chk('정답률을 함께 낸다', h.map(x => x.pct), [100, 100]);
  chk('없는 학생은 빈 목록', ctx.histOf('없는사람'), []);
  chk('이름이 없으면 빈 목록', ctx.histOf(''), []);
}

console.log('\n── 시트 기록이 더해진다 ──');
{
  reset();
  ctx.STORE.a = [rec('박바다', [1, 2, 3], 500, 3)];      // 이 폰에는 A회 하나뿐
  ctx.setHist([
    { examId: 'b', name: '박바다', answers: '111', ts: 200 },
    { examId: 'c', name: '박바다', answers: '44', ts: 300 },
  ], '박바다');
  const h = ctx.histOf('박바다');
  /* 순서는 회차 차례다(시각이 아니다). A·B·C 회 그대로. */
  chk('시트 것까지 세 회차', h.map(x => x.e.id), ['a', 'b', 'c']);
  chk('시트 기록도 채점된다', h.map(x => x.r.correct), [3, 3, 2]);
  /* 학부모 폰에서 링크 하나를 연 상황: 그 폰 기록은 1회지만 실제는 3회다 */
  chk('그 폰 기록만 세면 1회', Object.keys(ctx.STORE).length, 1);
}
{
  reset();
  /* 이름이 갈려 있어도 한 사람이다. 시트에도 그렇게 갈려 들어가 있다. */
  ctx.STORE.a = [rec('박바다', [1, 2, 3], 100, 3)];
  ctx.setHist([{ examId: 'b', name: '박 바다', answers: '111', ts: 200 }], '박바다');
  chk('공백이 달라도 같은 학생', ctx.histOf('박바다').map(x => x.e.id), ['a', 'b']);
  chk('반대로 물어도 같다', ctx.histOf('박 바다').length, 2);
}
{
  reset();
  ctx.STORE.a = [rec('박바다', [1, 2, 3], 100, 3)];
  ctx.setHist([{ examId: 'b', name: '박바다', answers: '111', ts: 200 }], '이아람');
  chk('다른 학생 것을 받아 왔으면 안 쓴다', ctx.histOf('박바다').map(x => x.e.id), ['a']);
}

console.log('\n── 한 회차는 한 번만 ──');
{
  reset();
  // 같은 회차를 두 번 채점(다시 풀었다) — 가장 최근 것만
  ctx.STORE.a = [rec('박바다', [1, 2, 3], 100, 3), rec('박바다', [1, 1, 1], 900, 1)];
  chk('가장 최근 응시', ctx.histOf('박바다').map(x => x.r.correct), [1]);

  reset();
  ctx.STORE.a = [rec('박바다', [1, 1, 1], 900, 1)];
  ctx.setHist([{ examId: 'a', name: '박바다', answers: '123', ts: 100 }], '박바다');
  chk('시트에 더 옛것이 있어도 최근 것', ctx.histOf('박바다').map(x => x.r.correct), [1]);
  chk('회차 수가 늘지 않는다', ctx.histOf('박바다').length, 1);
}

console.log('\n── 문항 수가 다르면 다른 시험이다 ──');
{
  reset();
  ctx.STORE.a = [rec('박바다', [1, 2], 100, 1)];                 // A회는 3문항인데 2개
  ctx.setHist([{ examId: 'c', name: '박바다', answers: '444', ts: 200 }], '박바다');  // C회는 2문항
  chk('길이가 어긋난 기록은 안 넣는다', ctx.histOf('박바다'), []);
  reset();
  ctx.setHist([{ examId: '없는회차', name: '박바다', answers: '123', ts: 1 }], '박바다');
  chk('모르는 회차는 넘긴다', ctx.histOf('박바다'), []);
  chk('답안이 없어도 안 죽는다',
      (ctx.setHist([{ examId: 'a', name: '박바다', ts: 1 }], '박바다'), ctx.histOf('박바다')), []);
}

console.log('\n── 회차 번호 순으로 늘어놓는다 ──');
{
  /* 선생님은 답안지를 모아 두었다가 하루에 몰아서 채점한다. 7/31 에
     3·8·9·10회를 넣으면 시각 순서로는 9 → 10 → 8 → 3 회가 된다 — 채점한
     순서일 뿐, 학생이 밟아 온 순서가 아니다. */
  ctx.FINAL_EXAMS = [
    { id: 'jmchc-1', title: 'JMChC 모의고사 1회', nQ: 3, key: [1, 1, 1] },
    { id: 'jmchc-3', title: 'JMChC 모의고사 3회', nQ: 3, key: [1, 1, 1] },
    { id: 'jmchc-9', title: 'JMChC 모의고사 9회', nQ: 3, key: [1, 1, 1] },
    { id: 'jmchc-10', title: 'JMChC 모의고사 10회', nQ: 3, key: [1, 1, 1] },
  ];
  ctx.STORE = {}; ctx.setHist(null, ''); ctx.resetOrd();
  ctx.STORE['jmchc-1'] = [rec('가', [1, 1, 1], 100, 3)];
  ctx.STORE['jmchc-9'] = [rec('가', [1, 1, 1], 900, 3)];    // 몰아 채점 — 9회를 먼저
  ctx.STORE['jmchc-10'] = [rec('가', [1, 1, 1], 901, 3)];
  ctx.STORE['jmchc-3'] = [rec('가', [1, 1, 1], 902, 3)];    // 3회를 맨 나중에
  chk('회차 번호 순', ctx.histOf('가').map(h => h.e.id), ['jmchc-1', 'jmchc-3', 'jmchc-9', 'jmchc-10']);
  chk('10회가 9회 뒤에 온다(글자 비교였다면 반대)',
      ctx.histOf('가').map(h => h.e.id).indexOf('jmchc-10') > ctx.histOf('가').map(h => h.e.id).indexOf('jmchc-9'), true);
}
{
  /* 갈래가 섞여도 갈래끼리 모인다. 갈래 안에서는 오름차순 —
     목록(exams.json)은 KMChC 기출을 최신부터 싣는데, 성장은 거꾸로다. */
  const mk = (id, title) => ({ id, title, nQ: 1, key: [1] });
  ctx.FINAL_EXAMS = [
    mk('jmchc-11', 'JMChC 모의고사 11회'), mk('jmchc-11-1', 'JMChC 모의고사 11-1회'),
    mk('jmchc-2', 'JMChC 모의고사 2회'),
    mk('donghyung-2', '기출동형 2회'), mk('donghyung-1', '기출동형 1회'),
    mk('kmchc-2026-1-ilban', 'KMChC 2026 제1차 · 일반'),
    mk('kmchc-2026-1-simhwa', 'KMChC 2026 제1차 · 심화'),
    mk('kmchc-2024-2', 'KMChC 2024 제2차'), mk('hwol-2024', 'KMChC 2024 제1차'),
    mk('hwol-2013', 'KMChC 2013'),
  ];
  ctx.resetOrd();
  chk('갈래끼리 · 갈래 안에서 오름차순',
      ctx.FINAL_EXAMS.slice().sort(ctx.cmpExam).map(e => e.id),
      ['jmchc-2', 'jmchc-11', 'jmchc-11-1', 'donghyung-1', 'donghyung-2',
       'hwol-2013', 'hwol-2024', 'kmchc-2024-2', 'kmchc-2026-1-ilban', 'kmchc-2026-1-simhwa']);
  chk('11회 다음이 11-1회', ctx.cmpExam(ctx.FINAL_EXAMS[0], ctx.FINAL_EXAMS[1]) < 0, true);
  chk('hwol-* 도 KMChC 갈래', [ctx.examFamily('hwol-2013'), ctx.examFamily('kmchc-2024-2')], ['kmchc', 'kmchc']);

  chk('축 이름을 짧게', ctx.FINAL_EXAMS.map(e => ctx.shortExam(e)),
      ['11회', '11-1회', '2회', '2회', '1회', '26년 1차', '26년 1차심', '24년 2차', '24년 1차', '13년']);
}

console.log('\n── 지금 보고 있는 회차를 집는다 ──');
{
  /* 시각 순일 때는 맨 뒤가 곧 이번 회차였다. 회차 순으로 늘어놓으면 아니다 —
     9회 성적표를 여는데 이력의 끝은 10회일 수 있다. '지난 진단 대비' 가
     엉뚱한 회차를 가리키면 학부모가 읽는 문장이 통째로 틀린다. */
  const h = [{ e: { id: 'a' } }, { e: { id: 'b' } }, { e: { id: 'c' } }];
  chk('가운데 회차를 집는다', ctx.histAt(h, { id: 'b' }), 1);
  chk('그 앞이 지난 진단', h[ctx.histAt(h, { id: 'b' }) - 1].e.id, 'a');
  chk('맨 앞이면 앞이 없다', ctx.histAt(h, { id: 'a' }), 0);
  chk('이력에 없으면 맨 뒤', ctx.histAt(h, { id: '없음' }), 2);

  // 시각으로 다시 정렬해 순서를 되돌리는 자리가 남아 있으면 안 된다
  chk('시각으로 다시 정렬하지 않는다', /hist\.sort\(\(a,b\)=>a\.ts-b\.ts\)/.test(SRC), false);
  chk('성장 추적이 보는 회차를 집는다',
      (SRC.match(/const _at=histAt\(hist,exam\);/g) || []).length, 2);
  chk('응시 여정도 보는 회차를 집는다', /const curR=rows\[histAt\(hist,exam\)\]/.test(SRC), true);
  chk('축이 회차다', /const xL=rows\.map\(r=>shortExam\(r\.h\.e\)\);/.test(SRC), true);
}

console.log('\n── 아홉 군데가 모두 한 곳을 쓴다 ──');
{
  /* 규칙을 베껴 쓰면 한 곳만 고쳐지고 나머지가 어긋난다. 실제로 그랬다.
     주석에는 옛 규칙이 설명으로 남아 있으므로 주석을 걷고 본다. */
  const CODE = SRC.replace(/\/\*[\s\S]*?\*\//g, '');
  chk('베낀 규칙이 남아 있지 않다',
      (CODE.match(/subs\(e\.id\)\.filter\([^\n]*r\.name/g) || []).length, 0);
  chk('여러 곳이 histOf 를 쓴다', (SRC.match(/histOf\(nm\)/g) || []).length >= 8, true);
}

console.log('\n── 시트 기록을 이 브라우저에 남기지 않는다 ──');
{
  /* 학부모 폰에 아이의 전 회차 답안을 남길 이유가 없다. 화면에 보여 줄 뿐이다. */
  const fn = cut(SRC, 'histOf');
  chk('histOf 가 저장하지 않는다', /saveSubs|localStorage\.setItem/.test(fn), false);
  const lh = cut(SRC, 'loadHist');
  chk('loadHist 도 저장하지 않는다', /saveSubs|localStorage\.setItem/.test(lh), false);
  chk('이름당 한 번만 묻는다', /if\(HIST_TRIED===key\) return;/.test(lh), true);
  chk('받으면 다시 그린다', /rerenderReport\(\)/.test(lh), true);
  chk('조용히 삼키지 않는다', /console\.error\('\[이력\]/.test(lh), true);
}

console.log('\n── 다시 그릴 때 되풀이하지 않는다 ──');
{
  const fn = cut(SRC, 'scoreAuto');
  chk('다시 그릴 때 저장하지 않는다', /if\(!again\) saveSubs\(cur\.id,arr\);/.test(fn), true);
  chk('다시 그릴 때 시트로 보내지 않는다', /if\(!again\) saveToSheetFinal\(/.test(fn), true);
  chk('다시 그릴 때 또 묻지 않는다', /if\(!again\) loadHist\(nm\);/.test(fn), true);
  /* 다시 그릴 때는 답안 입력칸이 이미 사라지고 성적표가 그 자리에 있다.
     칸을 그대로 읽으면 여기서 조용히 죽는다 — 실제로 그래서 화면이
     '2회 응시' 인 채로 남았다. */
  chk('칸이 없으면 성적표가 든 값을 쓴다',
      /el\? el\.value : \(\(window\.__rpt\|\|\{\}\)\[f\]\|\|''\)/.test(fn), true);
}

console.log('\n── 시트 쪽 창구 ──');
{
  chk('학생 단위 조회가 있다', /if \(p\.action === 'history'\) return historyFor_\(p\.name, cb\);/.test(GAS), true);
  /* 행을 읽는 자리는 한 학생만 뽑을 때(history)와 전부 뽑을 때(all)가 같다.
     두 벌로 두면 한쪽만 고쳐져 어긋난다 — 실제로 '학교·학년을 안 준다' 는
     버그가 list 쪽에만 있었다. 아래 규칙들은 그 한 자리를 본다. */
  chk('한 학생만 뽑을 때도 그 자리를 쓴다',
      /function historyFor_[\s\S]{0,300}_recordRows_\(key\)/.test(GAS), true);
  const fn = cut(GAS, '_recordRows_');
  chk('이름의 공백을 지우고 견준다', /_histKey_\(r\[1\]\) !== key/.test(fn), true);
  // 이름을 안 주면(all) 거르지 않는다. 여기가 뒤집히면 전체 조회가 빈 배열이다
  chk('이름을 안 주면 전부 준다', /if \(key && _histKey_/.test(fn), true);
  chk('답안이 없는 행은 넘긴다', /if \(!ans\) continue;/.test(fn), true);
  chk('앞에 붙은 따옴표를 뗀다', /replace\(\/\^'\/, ''\)/.test(fn), true);
  chk('저장시각을 함께 준다', /ts: \(r\[3\] instanceof Date\)/.test(fn), true);
  /* 시트에는 그때 쓰던 제목이 적혀 있다('화올 2018' → 'KMChC 2018').
     제목을 id 로 되돌리지 않으면 이름이 바뀐 회차의 옛 기록이 통째로 빠진다. */
  chk('제목을 회차 id 로 되돌린다', /var eid = _idOfTitle_\(r\[0\]\);/.test(fn), true);
  chk('못 되돌리면 넘긴다', /if \(!eid\) continue;/.test(fn), true);
  const rev = cut(GAS, '_idOfTitle_');
  chk('옛 제목도 표에서 찾는다', /if \(!\(ts instanceof Array\)\) ts = \[ts\];/.test(rev), true);
  chk('한 번만 뒤집어 둔다', /if \(!_TITLE2ID_\)/.test(rev), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
