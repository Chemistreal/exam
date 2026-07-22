/* ============================================================
   final.html 원점수 채점 규칙 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   규칙:
   - JMChC · 산과염기 : 정답 +3 / 무응답 0 / 오답 0   (무감점)
   - 그 외(화올·기출동형·KMChC 기출) : 정답 +3 / 무응답 0 / 오답 −1
   원점수 = 정답×3 − 오답×감점  (오답은 '찍었는데 틀린' 것만, 무응답 제외)

   실행:  node tests/final-score.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'final.html'), 'utf8');

// final.html에서 실제 채점 함수를 그대로 추출해 검증(구현과 테스트가 갈라지지 않게)
function grab(name) {
  const at = src.indexOf('function ' + name);
  if (at < 0) throw new Error(name + ' 없음');
  let i = src.indexOf('{', at), d = 0, j = i;
  for (; j < src.length; j++) { const c = src[j]; if (c === '{') d++; else if (c === '}' && --d === 0) { j++; break; } }
  return src.slice(at, j);
}
const _mk = new Function(grab('finalPenalty') + '\n' + grab('finalRawScore') +
  '\nreturn { finalPenalty: finalPenalty, finalRawScore: finalRawScore };');
const { finalPenalty, finalRawScore } = _mk();

let pass = 0, fail = 0;
function chk(desc, got, exp) {
  const ok = got === exp;
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc + ' → ' + JSON.stringify(got) + (ok ? '' : ' (기대 ' + JSON.stringify(exp) + ')'));
  ok ? pass++ : fail++;
}
function wrongList(nOman, nBlank) {
  const a = [];
  for (let i = 0; i < nOman; i++) a.push({ q: i + 1, a: 2 });   // 오답(1~4 골랐는데 틀림)
  for (let i = 0; i < nBlank; i++) a.push({ q: 100 + i, a: 0 }); // 무응답
  return a;
}

// 감점 대상 판별
chk('JMChC 무감점', finalPenalty({ group: 'JMChC' }), 0);
chk('산과염기 무감점', finalPenalty({ group: '산과염기' }), 0);
['화올', '동형', '2026', '2025', '2024', '이전'].forEach(g => chk(g + ' 감점', finalPenalty({ group: g }), 1));

// 원점수: 정답40 / 오답15 / 무응답5
chk('JMChC 원점수(40,15,5)', finalRawScore({ group: 'JMChC' }, 40, wrongList(15, 5)).score, 120);
chk('화올 원점수(40,15,5)', finalRawScore({ group: '화올' }, 40, wrongList(15, 5)).score, 105);
chk('KMChC(2024) 원점수(40,15,5)', finalRawScore({ group: '2024' }, 40, wrongList(15, 5)).score, 105);
// 무응답은 감점 없음
chk('화올 무응답만(정답50,무응답10)', finalRawScore({ group: '화올' }, 50, wrongList(0, 10)).score, 150);
// 만점
chk('화올 만점(60정답)', finalRawScore({ group: '화올' }, 60, wrongList(0, 0)).score, 180);

console.log('\n결과: ' + pass + ' pass / ' + fail + ' fail');
process.exit(fail ? 1 : 0);
