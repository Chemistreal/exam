/* ============================================================
   전원정답 문항 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   문제가 삭제·취소되거나 보기 넷이 모두 정답으로 인정되는 회차가 있다.
   그런 문항에는 **답안지에 아무것도 적혀 있지 않다** — 취소된 문제를 학생이
   굳이 풀어 두지 않았으니 당연하다. 그런데 앱은 답이 있어야만 맞은 것으로
   셌다. 전원정답 문항이 전원오답이 되어 있었다.

   그리고 분모. 예전에는 miss 문항을 채점에서 통째로 빼서 60문항짜리가
   59문항이 되었다. 시험은 60문항으로 치렀고, 삭제된 문항은 모두가 맞은
   것으로 처리하는 것이 채점의 관례다. 빼지 않고 더한다.

   여기서 지키는 것:
   - 답을 안 써도 맞은 것으로 센다
   - 무엇을 써도 맞은 것으로 센다
   - 분모(문항 수)에서 빠지지 않는다
   - 오답 감점을 먹지 않는다(틀린 것이 아니므로)
   - 보통 문항의 채점은 그대로다
   - 답안을 통째로 붙여 넣을 때 칸이 밀리지 않는다
   - 학생 제출 화면도 같은 규칙을 쓴다

   실행:  node tests/allcorrect.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const SUB = fs.readFileSync(path.join(ROOT, 'final-submit.html'), 'utf8');
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* 채점 규칙은 final.html 에서 그대로 오려 낸다 — 여기에 베껴 두면 둘이 갈라진다. */
function cutFrom(src, name) {
  const at = src.search(new RegExp(`^const ${name}=`, 'm'));
  if (at < 0) throw new Error(`${name} 을 못 찾았다`);
  const i = src.indexOf('{', at);
  const eol = src.indexOf('\n', at);
  if (i < 0 || i > eol) return src.slice(at, eol);       // 한 줄짜리
  let d = 0;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') d++;
    else if (src[j] === '}') { d--; if (!d) return src.slice(at, j + 1); }
  }
  throw new Error(`${name} 의 끝을 못 찾았다`);
}
function load(src) {
  const ctx = { console };
  vm.createContext(ctx);
  const names = ['accSet', 'allc', 'allcSet', 'okq'];
  // const 는 렉시컬이라 컨텍스트 객체에 안 붙는다 — 이름을 명시적으로 내보낸다
  vm.runInContext(names.map(n => cutFrom(src, n)).join('\n') +
    `\nObject.assign(globalThis,{${names.join(',')}});`, ctx);
  return ctx;
}
const F = load(SRC);

console.log('── 답이 없어도 맞은 것이다 ──');
{
  const e = { nQ: 3, key: [1, 2, 3], multi: { 2: [1, 2, 3, 4] } };
  chk('안 쓴 전원정답 문항이 정답', F.okq(e, 2, 0), true);
  chk('무엇을 써도 정답', [1, 2, 3, 4].map(a => F.okq(e, 2, a)), [true, true, true, true]);
  chk('보통 문항은 그대로 — 맞으면 정답', F.okq(e, 1, 1), true);
  chk('보통 문항은 그대로 — 틀리면 오답', F.okq(e, 1, 3), false);
  chk('보통 문항은 안 쓰면 오답', F.okq(e, 3, 0), false);
}
{
  // 삭제·취소된 문항은 miss 로 적혀 있다
  const e = { nQ: 3, key: [1, 2, 3], miss: [3] };
  chk('삭제된 문항도 안 써도 정답', F.okq(e, 3, 0), true);
  chk('삭제된 문항은 오답이 될 수 없다', F.okq(e, 3, 1), true);
}
{
  // 보기 둘만 인정하는 복수정답은 전원정답이 아니다
  const e = { nQ: 2, key: [1, 2], multi: { 1: [1, 3] } };
  chk('복수정답은 전원정답이 아니다', F.allc(e, 1), false);
  chk('인정하는 보기는 정답', [F.okq(e, 1, 1), F.okq(e, 1, 3)], [true, true]);
  chk('인정 밖 보기는 오답', F.okq(e, 1, 2), false);
  chk('복수정답도 안 쓰면 오답', F.okq(e, 1, 0), false);
}
{
  chk('빈 시험에도 안 죽는다', [F.allc({}, 1), F.allc(null, 1)], [false, false]);
  chk('전원정답 목록을 모은다',
      [...F.allcSet({ nQ: 5, miss: [5], multi: { 2: [1, 2, 3, 4], 4: [1, 3] } })].sort(), [2, 5]);
}

console.log('\n── 분모에서 빠지지 않는다 ──');
{
  /* 앱이 실제로 세는 방식과 같은 식으로 센다 — 문항 수 그대로 돌면서 okq 를 묻는다. */
  const e = { nQ: 60, key: Array(60).fill(1), miss: [60] };
  const sel = {};                       // 아무것도 안 쓴 답안
  let correct = 0, total = 0;
  for (let q = 1; q <= e.nQ; q++) { total++; if (F.okq(e, q, sel[q] || 0)) correct++; }
  chk('60문항이 60문항으로 남는다', total, 60);
  chk('삭제 문항 하나는 맞은 것으로 센다', correct, 1);

  // 소스가 실제로 그렇게 도는지 — 분모를 깎는 코드가 남아 있으면 안 된다
  chk('채점에서 문항을 빼지 않는다',
      /if\(miss\.has\(q\)\)continue; total\+\+/.test(SRC), false);
  chk('입력 화면이 문항 수를 그대로 쓴다', /const ac=allcSet\(cur\); const total=cur\.nQ;/.test(SRC), true);
  /* 진행 막대가 세는 것은 '채워 넣을 것' 이라 전원정답을 뺀다. 처음 그릴 때와
     입력 중에 세는 수가 다르면 첫 글자를 넣는 순간 숫자가 튄다. */
  chk('처음 그릴 때도 전원정답을 빼고 센다', /const need=total-ac\.size;/.test(SRC), true);
  chk('그 수를 화면에 쓴다', /progCount">0 \/ \$\{need\} 입력/.test(SRC), true);
}

console.log('\n── 오답 감점을 먹지 않는다 ──');
{
  /* 원점수 = 정답×3 − 감점×오답. 전원정답 문항은 오답 목록에 들어가지 않으므로
     감점 대상이 아니다. 오답 목록을 만드는 곳이 okq 를 쓰는지 확인한다. */
  const e = { nQ: 3, key: [1, 2, 3], group: '화올', miss: [3] };
  const sel = { 1: 1, 2: 4 };            // 1번 정답 · 2번 오답 · 3번 무응답(전원정답)
  const wrong = [];
  let correct = 0;
  for (let q = 1; q <= e.nQ; q++) { const a = sel[q] || 0; if (F.okq(e, q, a)) correct++; else wrong.push({ q, a }); }
  chk('전원정답은 오답 목록에 없다', wrong.map(w => w.q), [2]);
  chk('맞은 문항 수', correct, 2);
  // finalRawScore 로 실제 점수까지
  const mk = new Function(
    SRC.slice(SRC.indexOf('function finalPenalty')).slice(0, 400).split('\n').slice(0, 1).join('\n') + '\n' +
    (() => { const at = SRC.indexOf('function finalRawScore'); let i = SRC.indexOf('{', at), d = 0;
      for (let j = i; j < SRC.length; j++) { if (SRC[j] === '{') d++; else if (SRC[j] === '}' && !--d) return SRC.slice(at, j + 1); } })() +
    '\nreturn finalRawScore;')();
  chk('정답 2 · 오답 1 → 6−1=5점', mk(e, correct, wrong).score, 5);
}

console.log('\n── 붙여 넣을 때 칸이 밀리지 않는다 ──');
{
  /* 예전에는 잠긴 칸을 건너뛰며 채웠다. 60개를 붙여 넣으면 그 뒤가 통째로
     한 칸씩 밀려서, 삭제 문항 뒤 문항들이 전부 남의 답으로 채워졌다. */
  chk('건너뛰며 채우지 않는다', /while\(i<=cur\.nQ&&miss\.has\(i\)\) i\+\+/.test(SRC), false);
  chk('붙인 자리부터 1:1 로 채운다',
      /for\(const ch of raw\)\{ if\(i>cur\.nQ\)break; setAns\(i,\+ch\); i\+\+; \}/.test(SRC), true);
  chk('칸을 잠그지 않는다', /placeholder="\$\{m\?'◎':'·'\}"[^>]*disabled/.test(SRC), false);
  chk('학생 화면도 칸을 잠그지 않는다', /maxlength="1" '\+\(m\?'disabled'/.test(SUB), false);
}

console.log('\n── 학생 제출 화면도 같은 규칙이다 ──');
{
  const S = load(SUB);
  const e = { nQ: 3, key: [1, 2, 3], miss: [3], multi: { 2: [1, 2, 3, 4] } };
  chk('안 쓴 전원정답이 정답', [S.okq(e, 2, 0), S.okq(e, 3, 0)], [true, true]);
  chk('보통 문항은 그대로', [S.okq(e, 1, 1), S.okq(e, 1, 2)], [true, false]);
  // 두 파일의 규칙이 문자 그대로 같아야 한다 — 한쪽만 고치면 점수가 갈린다
  const norm = s => s.replace(/\s+/g, ' ').trim();
  chk('두 화면의 okq 가 같다', norm(cutFrom(SRC, 'okq')), norm(cutFrom(SUB, 'okq')));
  chk('두 화면의 allc 가 같다', norm(cutFrom(SRC, 'allc')), norm(cutFrom(SUB, 'allc')));
}

console.log('\n── 실제 회차 데이터로 ──');
{
  const withAllc = EXAMS.filter(e => F.allcSet(e).size > 0);
  chk('전원정답 문항이 있는 회차가 있다', withAllc.length > 0, true);
  // 전원정답 문항의 정답 키는 아무 의미가 없다 — 없어도(0) 되고 있어도 된다
  const outOfRange = [];
  EXAMS.forEach(e => { [...F.allcSet(e)].forEach(q => { if (q < 1 || q > e.nQ) outOfRange.push(`${e.id}:${q}`); }); });
  chk('전원정답 문항 번호가 범위 안이다', outOfRange, []);
  // 한 회차가 통째로 전원정답이면 채점이 뜻을 잃는다 — 데이터 실수를 잡는다
  const allGiven = EXAMS.filter(e => F.allcSet(e).size >= e.nQ).map(e => e.id);
  chk('통째로 전원정답인 회차는 없다', allGiven, []);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
