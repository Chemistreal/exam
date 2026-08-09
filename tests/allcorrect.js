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
  /* 원본 정답표에 '문제삭제' 로 적힌 문항(voided)이다. 여태 채점 규칙은 이
     칸을 **안 봤다** — 폐기 문항 여섯에 마침 multi:[1,2,3,4] 나 key:0 이 같이
     적혀 있어서 그 갈래로 걸렸을 뿐이다. 우연이 규칙 노릇을 하고 있었다.
     voided 에만 적힌 문항은 조용히 보통 문항으로 채점된다 — 답을 안 쓴
     학생 전원이 오답이 된다. 삭제는 곧 전원정답이라고 못박는다. */
  const e = { nQ: 3, key: [1, 2, 3], voided: [2] };
  chk('삭제(voided)만 적혀 있어도 전원정답', F.allc(e, 2), true);
  chk('삭제된 문항은 안 써도 정답', F.okq(e, 2, 0), true);
  chk('삭제된 문항은 무엇을 써도 정답', [1, 2, 3, 4].map(a => F.okq(e, 2, a)), [true, true, true, true]);
  chk('삭제 문항이 목록에 들어간다', [...F.allcSet(e)].sort(), [2]);
  chk('학생 화면도 같은 규칙', [...load(SUB).allcSet(e)].sort(), [2]);
  chk('옆 문항은 그대로', [F.okq(e, 1, 1), F.okq(e, 1, 2)], [true, false]);
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

console.log('\n── 정답이 X 인 문항도 전원정답 ──');
{
  /* 정답키 자리가 비어 있으면(0 · '' · X) 답이 정해지지 않은 문항이다.
     정해지지 않은 답을 틀렸다고 할 수는 없다. */
  const e = { nQ: 4, key: [1, 0, 'X', ''] };
  chk('0 은 전원정답', [F.allc(e, 2), F.okq(e, 2, 0), F.okq(e, 2, 3)], [true, true, true]);
  chk("'X' 도 전원정답", F.okq(e, 3, 0), true);
  chk('빈칸도 전원정답', F.okq(e, 4, 0), true);
  chk('정답이 있는 문항은 그대로', [F.okq(e, 1, 1), F.okq(e, 1, 2)], [true, false]);
  chk('목록에도 들어간다', [...F.allcSet(e)].sort(), [2, 3, 4]);

  /* 정답키 배열이 통째로 없는 것은 다른 이야기다. 아직 안 들어온 데이터이지
     전원정답이 아니다 — 그렇게 세면 회차 하나가 통째로 만점이 된다. */
  chk('정답키가 없으면 전원정답이 아니다',
      [F.allc({ nQ: 3 }, 1), F.allc({ nQ: 3, key: [] }, 1)], [false, false]);
  chk('범위 밖은 전원정답이 아니다', F.allc(e, 9), false);
  chk('학생 화면도 같다', [...load(SUB).allcSet(e)].sort(), [2, 3, 4]);
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

  /* 어느 문항이 전원정답인지를 통째로 못 박아 둔다.
     이 규칙은 miss·multi·정답키 세 곳에서 파생되므로, 어느 하나를 손볼 때
     엉뚱한 문항이 딸려 들어오기 쉽다. 선생님이 지목하지 않은 문항이 조용히
     만점 처리되면 아무도 눈치채지 못한 채 성적이 바뀐다.
     회차를 새로 넣거나 전원정답을 지정할 때는 이 표를 **의도해서** 고친다. */
  const PINNED = {
    'jmchc-4': [36], 'jmchc-7': [33], 'jmchc-9': [47, 50, 60], 'jmchc-10': [50],
    'donghyung-2': [19], 'kmchc-2025-1-simhwa': [38, 41],
    'hwol-2021': [60], 'hwol-2019': [23, 42], 'hwol-2018': [34],
    'hwol-2017': [60], 'hwol-2015': [20], 'hwol-2014': [57],
    'hwol-2010': [38, 42],   // 대회 원본 정답표에 '삭제' 로 적힌 두 문항
    'hwol-2009': [51],       // 옳은 보기가 하나뿐인데 그 답지가 없어 전원정답
  };
  const actual = {};
  EXAMS.forEach(e => { const s = [...F.allcSet(e)].sort((a, b) => a - b); if (s.length) actual[e.id] = s; });
  chk('전원정답 문항 목록이 그대로다', actual, PINNED);
}

console.log('\n── 읽는 쪽에도 "빠졌다" 고 말하지 않는다 ──');
{
  /* 채점은 더하는데 화면은 빼는 것처럼 말하고 있었다.

       문항별 정오표    정오 칸에 '제외' · 정답 칸은 '-'
       DOCX 정오표      칸 표시가 '–' · 범례가 '채점 제외'
       방법론 ②         "정답 미확정 문항은 분모에서 제외" ← 사실과 다르다
       해설지           '→ 채점 제외' (hwol-2009 51번)
       해설 목차        딱지가 '삭제' 와 '전원' 으로 갈려 있었다

     60문항짜리에서 '제외' 둘을 본 학부모는 58문항으로 친 줄 안다. 삭제는
     빼는 것이 아니라 **모두 맞은 것으로 처리하는 것**이다(선생님 결정,
     2026-08-09). 읽는 쪽 문서에서 그 말이 되살아나면 여기서 잡는다. */
  const FILES = ['final.html', 'sample_report.html', 'index_haeseol.html'];
  fs.readdirSync(ROOT).forEach(f => { if (/^sol-final-.*\.html$/.test(f)) FILES.push(f); });
  /* ⚠ 처음에는 '채점 제외' 다섯 글자만 막았는데, 해설 본문은 띄어쓰기가
     달라서(채점**에서** 제외 · 채점**서** 제외) 그대로 빠져나갔다. 학생이
     읽는 것은 문구지 상수가 아니다 — 어미가 붙은 꼴까지 막는다. */
  const BAN = [/채점\s*(?:에서\s*|서\s*)?제외/, /채점제외/, />제외</, /분모에서\s*제외/];
  const hits = [];
  FILES.forEach(f => {
    const t = fs.readFileSync(path.join(ROOT, f), 'utf8');
    BAN.forEach(w => { const m = t.match(w); if (m) hits.push(`${f}: ${m[0]}`); });
  });
  chk('성적표·해설지에 "채점에서 제외" 라는 말이 없다', hits, []);
  // 해설 목차의 딱지 이름은 한 가지다
  const idx = fs.readFileSync(path.join(ROOT, 'index_haeseol.html'), 'utf8');
  chk('목차 딱지에 "삭제" 가 없다', /<span class="sp">삭제/.test(idx), false);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
