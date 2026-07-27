/* ============================================================
   final-submit.html ↔ final.html 공유 코드 동기화 검사
   ------------------------------------------------------------
   학생 제출 페이지(final-submit.html)는 채점·시트 전송이 교사용
   final.html과 100% 같도록, 채점 함수·엔드포인트를 그대로 복사해 쓴다.
   한쪽만 고치면 학생 채점이 교사 채점과 달라진다.
   이 검사는 공유 심볼을 두 파일에서 추출해 서로 다르면 실패한다.

   [바뀐 것] 정답키(FINAL_EXAMS)는 이제 복사하지 않는다. 두 파일 모두
   `exams.json` 을 받아 쓰므로 갈라질 자리가 없어졌다. 대신 두 파일이
   정말로 그 파일을 받아 쓰는지, 사본이 되살아나지 않았는지를 본다.

   실행:  node tests/final-submit-sync.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const A = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const B = fs.readFileSync(path.join(ROOT, 'final-submit.html'), 'utf8');

const FN = ['finalPenalty', 'finalRawScore', 'percentile', 'award', 'hashStrFinal'];
const CO = ['RX', 'RXMAP', 'TIERS', 'accSet', 'okq', 'SHEET_ENDPOINT'];

function grabFn(src, n) {
  const at = src.search(new RegExp('function\\s+' + n + '\\s*\\('));
  if (at < 0) return null;
  let i = src.indexOf('{', at), d = 0, j = i;
  for (; j < src.length; j++) { const c = src[j]; if (c === '{') d++; else if (c === '}' && --d === 0) { j++; break; } }
  return src.slice(at, j);
}
function grabConst(src, n) {
  const at = src.search(new RegExp('const\\s+' + n + '\\s*='));
  if (at < 0) return null;
  let i = src.indexOf('=', at), d = 0, j = i + 1, s = null;
  for (; j < src.length; j++) {
    const c = src[j], p = src[j - 1];
    if (s) { if (c === s && p !== '\\') s = null; continue; }
    if (c === '"' || c === "'" || c === '`') { s = c; continue; }
    if ('{[('.includes(c)) d++; else if ('}])'.includes(c)) d--;
    else if (c === ';' && d === 0) { j++; break; }
  }
  return src.slice(at, j);
}

let pass = 0, fail = 0;
function chk(name, a, b) {
  if (a == null) { console.log('  FAIL  ' + name + ' — final.html에 없음'); fail++; return; }
  if (b == null) { console.log('  FAIL  ' + name + ' — final-submit.html에 없음'); fail++; return; }
  const ok = a === b;
  console.log((ok ? '  PASS  ' : '  FAIL  ') + name + (ok ? '' : ' — 두 파일 내용 다름(드리프트)'));
  ok ? pass++ : fail++;
}

CO.forEach(n => chk(n, grabConst(A, n), grabConst(B, n)));
FN.forEach(n => chk(n, grabFn(A, n), grabFn(B, n)));

/* 정답키는 이제 exams.json 한 곳에만 있다. 사본이 되살아나면 여기서 걸린다. */
function chk2(name, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + name +
    (ok ? '' : ' → ' + JSON.stringify(got) + ' (기대 ' + JSON.stringify(want) + ')'));
  ok ? pass++ : fail++;
}
const exams = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
chk2('exams.json 에 시험이 들어 있다', exams.length > 0, true);
[['final.html', A], ['final-submit.html', B]].forEach(([name, src]) => {
  chk2(name + ' 이 exams.json 을 받아 온다', /fetch\('exams\.json'/.test(src), true);
  // `const FINAL_EXAMS=[{...}]` 처럼 사본을 다시 박아 넣지 않았는지
  chk2(name + ' 에 시험 목록 사본이 없다', /FINAL_EXAMS\s*=\s*\[\s*\{/.test(src), false);
});

console.log('\n결과: ' + pass + ' 일치 / ' + fail + ' 불일치');
process.exit(fail ? 1 : 0);
