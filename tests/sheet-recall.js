/* ============================================================
   **시트에 쌓인 줄이 앱으로 돌아오는가** — 순수 node
   ------------------------------------------------------------
   시트는 회차를 **제목 문자열**로 적는다. 앱은 회차 id 로 다룬다. 그 사이를
   EXAM_TITLES 라는 손으로 적는 표가 잇는데, `_recordRows_` 는 그 표에서 제목을
   못 찾으면 그 줄을 **통째로 버린다**.

   그래서 표 밖에서 생긴 회차 — 학생별 파이널(변형본 60제 · 실전 30제 ·
   즉시 재도전 10제) — 는 이런 꼴이었다:

     · 학생이 제출한다 → 시트에 줄이 **멀쩡히 쌓인다**
     · 선생님이 「시트에서 불러오기 ↓」 를 누른다 → «시트와 이미 같습니다»
     · 학생 성적표의 «누적 N회» 에도 안 세어진다
     · 시트를 열어 보면 줄은 거기 있다

   기록이 사라진 것도 아닌데 아무 데서도 안 보이니, 선생님은 학생이 시험을
   안 봤다고 읽는다. 아홉 명이 오늘 밤 이 회차로 제출한다.

   고침: 제목으로 못 찾으면 **공유링크**(`#r=<회차id>.<답안>`)에서 꺼낸다.
   그건 기계가 적은 것이라 새 회차에도, 옛 줄에도 이미 들어 있다.

   여기서 지키는 것
   ----------------
     · 표에 있는 제목은 **여전히 표가 이긴다**(이름 바뀐 회차의 옛 기록을
       새 id 로 모으는 일은 표만 할 수 있다)
     · 표에 없는 학생별 회차도 링크에서 id 를 찾아 돌아온다
     · 봉투(`#x=…&r=…`)가 앞에 붙어도 찾는다
     · 아무 데서도 못 찾으면 **버린다**(엉뚱한 회차로 섞느니 빠지는 게 낫다)

   실행:  node tests/sheet-recall.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const gs = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let pass = 0, fail = 0;
function chk(desc, got, exp) {
  const ok = JSON.stringify(got) === JSON.stringify(exp);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc +
    (ok ? '' : ' → ' + JSON.stringify(got) + ' (기대 ' + JSON.stringify(exp) + ')'));
  ok ? pass++ : fail++;
}

/* 구현을 그대로 떼어 온다 — 검사가 제 나름의 사본을 들고 갈라지지 않게. */
function cut(from, to) {
  const a = gs.indexOf(from);
  if (a < 0) throw new Error('없다: ' + from);
  const b = gs.indexOf(to, a);
  return gs.slice(a, b + to.length);
}
const src = cut('var EXAM_TITLES = {', '\n};')
  + '\n' + cut('var _TITLE2ID_ = null;', 'return _TITLE2ID_[String(title || \'\')] || \'\';\n}')
  + '\n' + cut('function _idOfLink_(link)', 'return _idOfTitle_(r[0]) || _idOfLink_(r[2]);\n}');
const M = new Function(src +
  ';return {idOfTitle:_idOfTitle_, idOfLink:_idOfLink_, idOfRow:_idOfRow_, T:EXAM_TITLES};')();

const BASE = 'https://chemistreal.github.io/exam/final.html';

/* ── ① 표가 여전히 이긴다 ── */
console.log('── 표에 있는 제목 ──');
const known = Object.keys(M.T)[0];
const knownTitle = [].concat(M.T[known])[0];
chk('표에 있는 제목은 표에서 나온다', M.idOfRow([knownTitle, '홍길동', '']), known);
/* 링크가 다른 회차를 가리켜도 표가 이긴다 — 이름이 바뀐 회차를 모으는 일. */
chk('표가 링크보다 먼저다',
  M.idOfRow([knownTitle, '홍길동', BASE + '#r=zzz-other.1a']), known);

/* ── ② 표 밖의 학생별 회차 ── */
console.log('\n── 표에 없는 학생별 회차 ──');
const CASES = [
  ['실전 30제 · s2p0c114x5f2', BASE + '#r=s2p0c114x5f2-3.28fnq.。.7ZWQ', 's2p0c114x5f2-3'],
  ['파이널 변형본 60제 · s4w000h6h6l0', BASE + '#r=s4w000h6h6l0-2.9zz', 's4w000h6h6l0-2'],
  ['즉시 재도전 10제 · s6w2y5y2i485', BASE + '#r=s6w2y5y2i485-4.3k', 's6w2y5y2i485-4'],
];
for (const [title, link, want] of CASES) {
  chk('«' + title + '» 이 돌아온다', M.idOfRow([title, '홍길동', link]), want);
  chk('  제목만으로는 못 찾는다(그래서 링크가 필요했다)', M.idOfTitle(title), '');
}

/* ── ③ 봉투가 앞에 붙어도 ── */
console.log('\n── 즉석 재도전(봉투가 앞에 오는 링크) ──');
chk('#x=…&r=… 에서도 찾는다',
  M.idOfRow(['즉석 재도전 10제 · s32243g212j0',
    '홍길동', BASE + '#x=czMyMjQzZzIxMmowfDEyMzQ&r=s32243g212j0-rab12.7h']),
  's32243g212j0-rab12');

/* ── ④ 못 찾으면 버린다 ── */
console.log('\n── 아무 데서도 못 찾는 줄 ──');
chk('링크가 없으면 빈 값', M.idOfRow(['알 수 없는 시험', '홍길동', '']), '');
chk('r= 이 없는 링크면 빈 값',
  M.idOfRow(['알 수 없는 시험', '홍길동', BASE + '#n=abc']), '');
chk('id 뒤에 점이 없으면 안 믿는다',
  M.idOfRow(['알 수 없는 시험', '홍길동', BASE + '#r=s2p0c114x5f2-3']), '');

/* ── ⑤ 오늘 실제로 쓰는 회차가 전부 걸린다 ── */
console.log('\n── 오늘 쓰는 학생별 회차 전수 ──');
const sf = JSON.parse(fs.readFileSync(path.join(ROOT, 'student-finals.json'), 'utf8'));
const miss = (sf.exams || []).filter(e => {
  const link = BASE + '#r=' + e.id + '.1a2b';
  return M.idOfRow([e.title, '홍길동', link]) !== e.id;
});
chk('학생별 회차 ' + (sf.exams || []).length + '개가 모두 제 id 로 돌아온다',
  miss.map(e => e.id), []);

/* ── ⑥ _recordRows_ 가 실제로 링크 갈래를 쓴다 ── */
console.log('\n── 구현이 정말 그 갈래를 쓰는가 ──');
chk('_recordRows_ 가 _idOfRow_ 를 부른다',
  /var eid = _idOfRow_\(r\);/.test(gs), true);
chk('옛 _idOfTitle_ 직접 호출이 안 남았다',
  /var eid = _idOfTitle_\(r\[0\]\);/.test(gs), false);

console.log('\n' + (fail ? `실패 ${fail}건 / 통과 ${pass}건`
  : `통과 ${pass}건 — 시트에 쌓인 줄이 앱으로 돌아온다.`));
process.exit(fail ? 1 : 0);
