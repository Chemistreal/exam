/* ============================================================
   창구가 보내온 점수를 **다시 센다** — 회귀 테스트
   ------------------------------------------------------------
   채점은 전부 브라우저에서 일어나고, 그 결과가 그대로 시트로 온다. 여태
   창구에는 정답표가 없어서 보내온 수가 맞는지 가릴 방법이 아예 없었다.
   누구든 아무 이름으로 만점을 올릴 수 있고, 그런 줄 몇 개면 다른 학생의
   석차·백분위·또래 정답률이 전부 흔들린다 — 실제로 그런 일이 있었다.

   ⚠ 고치지는 않는다. 어긋난 줄만 `검증기록` 에 남긴다. 창구가 말없이
     점수를 갈아 치우면 그게 더 위험하다 — 나중에 전원정답으로 돌린
     회차에서는 옛 줄이 통째로 「틀린 것」이 된다.

   여기서 지키는 것:
   - 다시 세는 규칙이 화면의 채점 규칙(okq)과 **글자 그대로 같다**
     → 전 회차·전 문항을 실제 답안으로 맞대어 본다. 하나라도 다르면 FAIL
   - 전원정답(miss·voided·multi 넷)은 무엇을 써도, 안 써도 맞는다
   - 복수정답은 그 답들만 맞는다
   - 모르는 회차·길이가 다른 답안은 **판정하지 않는다**(null)
   - 점수를 고치는 자리가 없다

   실행:  node tests/server-regrade.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) fail++;
  console.log((ok ? '  ok   ' : '  FAIL ') + n +
    (ok ? '' : `\n         받은 것: ${JSON.stringify(got)}\n         바란 것: ${JSON.stringify(want)}`));
};

const ctx = vm.createContext(require('./_gasenv')({}));
for (const re of [/var EXAM_KEYS = \{[\s\S]*?\n\};/, /function _verifyCorrect_\([\s\S]*?\n\}/]) {
  const m = GAS.match(re);
  if (!m) { console.log('  FAIL .gs 에서 못 찾았다: ' + re); fail++; }
  else vm.runInContext(m[0], ctx);
}
const verify = (title, ans) =>
  vm.runInContext('_verifyCorrect_(' + JSON.stringify(title) + ',' + JSON.stringify(ans) + ')', ctx);

/* ── 화면의 채점 규칙을 그대로 옮겨 온 것 (final.html:1096·1111·1131) ──
   여기 옮겨 적은 것이 저기와 어긋나면 이 검사가 거짓말을 한다. 그래서
   아래에서 final.html 의 그 세 줄이 안 바뀌었는지도 함께 본다. */
const accSet = (e, q) => (e.multi && e.multi[q]) ? e.multi[q] : [e.key[q - 1]];
const allc = (e, q) => {
  if (e.miss && e.miss.indexOf(q) >= 0) return true;
  if (e.voided && e.voided.indexOf(+q) >= 0) return true;
  const m = e.multi && e.multi[q];
  if (m && m.length >= 4) return true;
  return false;
};
const okq = (e, q, a) => allc(e, q) || accSet(e, q).indexOf(a) >= 0;

console.log('화면의 채점 규칙과 글자 그대로 같은가 — 전 회차 · 전 문항');
let mismatch = [], seen = 0;
for (const e of EXAMS) {
  const n = e.nQ || (e.key || []).length;
  if (!n || !e.key) continue;
  /* 답안 다섯 벌을 만들어 본다: 정답 그대로 · 한 칸씩 민 것 · 전부 1 ·
     전부 4 · 무응답. 전원정답과 복수정답이 있는 자리가 여기서 드러난다. */
  const sheets = [
    Array.from({ length: n }, (_, i) => e.key[i] || 0),
    Array.from({ length: n }, (_, i) => ((e.key[i] || 1) % 4) + 1),
    Array.from({ length: n }, () => 1),
    Array.from({ length: n }, () => 4),
    Array.from({ length: n }, () => 0),
  ];
  for (const sel of sheets) {
    let want = 0;
    for (let q = 1; q <= n; q++) if (okq(e, q, sel[q - 1])) want++;
    const got = verify(e.title, sel.join(''));
    seen++;
    if (got !== want) mismatch.push(`${e.id} [${sel.slice(0, 4).join('')}…] 창구 ${got} ≠ 화면 ${want}`);
  }
}
chk(`${seen}벌을 맞대어 다른 것이 없다`, mismatch.slice(0, 6), []);
chk('맞대어 본 답안이 넉넉하다', seen >= 200, true);

console.log('\n전원정답 · 복수정답');
const voided = EXAMS.find(e => (e.voided || []).length || (e.miss || []).length);
if (voided) {
  const q = (voided.voided || voided.miss)[0];
  const n = voided.nQ || voided.key.length;
  const blank = Array.from({ length: n }, () => 0);
  const c0 = verify(voided.title, blank.join(''));
  const one = blank.slice(); one[q - 1] = 1;
  const c1 = verify(voided.title, one.join(''));
  chk(`${voided.id} ${q}번은 안 써도 맞는다`, c0 >= 1, true);
  chk(`${voided.id} ${q}번은 무엇을 써도 같다`, c1, c0);
} else {
  console.log('  --   전원정답 문항이 있는 회차가 없다(넘어간다)');
}
const multi = EXAMS.find(e => Object.keys(e.multi || {}).some(k => (e.multi[k] || []).length === 2));
if (multi) {
  const q = Object.keys(multi.multi).find(k => multi.multi[k].length === 2);
  const n = multi.nQ || multi.key.length;
  const base = Array.from({ length: n }, () => 0);
  const scores = [1, 2, 3, 4].map(a => { const s = base.slice(); s[+q - 1] = a; return verify(multi.title, s.join('')); });
  const okCount = scores.filter(v => v > scores.reduce((m, x) => Math.min(m, x), 99)).length;
  chk(`${multi.id} ${q}번은 둘만 인정한다`, okCount, 2);
} else {
  console.log('  --   복수정답이 둘인 회차가 없다(넘어간다)');
}

console.log('\n모르면 판정하지 않는다');
chk('없는 회차는 null', verify('있을 리 없는 시험 제목', '111111'), null);
chk('길이가 다르면 null', verify(EXAMS[0].title, '111'), null);
chk('답안이 없으면 null', verify(EXAMS[0].title, ''), null);
chk("앞의 작은따옴표를 떼고 읽는다",
    verify(EXAMS[0].title, "'" + EXAMS[0].key.join('')),
    verify(EXAMS[0].title, EXAMS[0].key.join('')));

console.log('\n점수를 고치지 않는다');
const post = (() => {
  const i = GAS.indexOf('function doPost(e) {');
  let d = 0;
  for (let j = i; j < GAS.length; j++) {
    if (GAS[j] === '{') d++;
    else if (GAS[j] === '}' && --d === 0) return GAS.slice(i, j + 1);
  }
  return GAS.slice(i);
})();
chk('다시 센 값을 시트 줄에 안 쓴다', /row\s*\[\s*\d+\s*\]\s*=\s*again/.test(post), false);
chk('어긋나면 검증기록에만 남긴다', /_logVerify_\(/.test(post), true);
chk('세다 터져도 채점은 이어진다', /catch \(eV\)/.test(post), true);
/* 성적기록에 줄을 더하면 석차·백분위 모집단이 흔들린다. 다른 시트여야 한다. */
const fnBody = (name) => {
  /* 글자 수로 자르면 다음 함수까지 딸려 온다 — 괄호를 세어 닫는 자리를 찾는다. */
  const i = GAS.indexOf('function ' + name + '(');
  let d = 0;
  for (let j = i; j < GAS.length; j++) {
    if (GAS[j] === '{') d++;
    else if (GAS[j] === '}' && --d === 0) return GAS.slice(i, j + 1);
  }
  return GAS.slice(i);
};
const logf = fnBody('_logVerify_');
chk('검증기록이라는 다른 시트에 남긴다', /getSheetByName\('검증기록'\)/.test(logf), true);
chk('성적기록에는 안 쓴다', /성적기록/.test(logf), false);

/* 위에 옮겨 적은 규칙이 화면의 그것과 같은지 — 저쪽이 바뀌면 여기가 거짓이 된다. */
console.log('\n옮겨 적은 규칙이 화면과 같은가');
const FIN = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8').replace(/\s/g, '');
for (const line of [
  "constaccSet=(e,q)=>(e.multi&&e.multi[q])?e.multi[q]:[e.key[q-1]];",
  "constokq=(e,q,a)=>allc(e,q)||accSet(e,q).indexOf(a)>=0;",
]) chk('화면에 그대로 있다: ' + line.slice(0, 28) + '…', FIN.includes(line), true);

console.log(fail ? `\n${fail}건 어긋났다` : '\n다 맞다');
process.exit(fail ? 1 : 0);
