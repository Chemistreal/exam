/* ============================================================
   갈라진 이름표 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   성적표는 이름이 **정확히 같은** 기록만 한 학생으로 본다. final.html 안에서
   아홉 군데가 같은 규칙을 쓴다:

       subs(e.id).filter(r => r.name.trim() === nm && r.ans.length === e.nQ)

   그래서 '박 바다' 처럼 공백 하나, 글자 하나가 어긋난 기록은 조용히 빠졌다.

   **띄어쓰기는 이제 저장할 때 붙인다**(nameKey). 기계가 확실히 판단할 수 있는
   것은 기계가 하고, 사람이 봐야 하는 것만 남긴다 — 한 글자가 다른 이름은
   동명이인일 수 있어서 기계가 합치면 되돌릴 수 없다.
   화면은 "진단 6회 누적" 이라고 **단언하고**, 첫 회차만 갈라져 있으면
   학부모에게 나가는 종이에 "첫 진단입니다" 라고 적힌다. 읽는 쪽에는 빠졌다는
   신호가 어디에도 없다 — 선생님이 "3·4회 봤다던데" 하고 되물어야만 드러난다.

   고칠 수 있는 것은 합치는 일(명단 관리)이지만, **모르면 합칠 수도 없다.**
   그래서 성적표가 먼저 말한다.

   여기서 지키는 것:
   - 띄어쓰기 차이는 저절로 붙는다(경고하지 않는다)
   - 한 글자 다른 이름은 찾아서 사람에게 보여 준다(합치지는 않는다)
   - 남남인 이름은 끌어오지 않는다(경고가 흔해지면 아무도 안 읽는다)
   - 같은 시험이 두 ID 로 등록돼 있어도 두 번 세지 않는다
   - 갈라진 기록이 있으면 '첫 진단' 이라고 단언하지 않는다
   - 어느 브라우저 기준인지 밝힌다

   실행:  node tests/split-name.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};
function cut(name) {
  const at = SRC.search(new RegExp(`^function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`final.html 에서 ${name} 을 못 찾았다`);
  let d = 0;
  for (let j = SRC.indexOf('{', at); j < SRC.length; j++) {
    if (SRC[j] === '{') d++;
    else if (SRC[j] === '}') { d--; if (!d) return SRC.slice(at, j + 1); }
  }
  throw new Error(`${name} 의 끝을 못 찾았다`);
}

/* subs·FINAL_EXAMS 는 브라우저 것이라 여기서 대신 세운다. cohortKey 는
   원본을 그대로 쓴다 — 별칭 규칙이 바뀌면 여기서 걸려야 한다. */
const ctx = { console, STORE: {}, FINAL_EXAMS: [] };
vm.createContext(ctx);
vm.runInContext([
  SRC.match(/^const COHORT_ALIAS=.*$/m)[0],
  SRC.match(/^const cohortKey=.*$/m)[0],
  SRC.match(/^const nameKey=.*$/m)[0],
  cut('editDist'),
  'function subs(id){ return STORE[cohortKey(id)] || []; }',
  cut('splitNameRecords'),
  'Object.assign(globalThis,{splitNameRecords, cohortKey, COHORT_ALIAS, nameKey});',
].join('\n'), ctx);

const setup = (exams, store) => { ctx.FINAL_EXAMS = exams; ctx.STORE = store; };
const rec = name => ({ name, ans: [1, 2, 3], correct: 1, total: 3 });

console.log('── 띄어쓰기는 저절로 붙는다 ──');
{
  /* 저장할 때 nameKey 가 공백을 지우므로 애초에 갈라지지 않는다. 이미 쌓인
     기록도 tidyNames 가 한 번 다듬는다. 그러니 여기서 경고할 것이 아니다 —
     고칠 것이 없는데 뜨는 경고는 다음 경고까지 못 읽게 만든다. */
  chk('공백을 지운다', ctx.nameKey('박 바다'), '박바다');
  chk('여러 칸도', ctx.nameKey('박  바 다'), '박바다');
  chk('앞뒤 공백도', ctx.nameKey('  박바다 '), '박바다');
  chk('빈 값에도 안 죽는다', [ctx.nameKey(null), ctx.nameKey(undefined), ctx.nameKey('')], ['', '', '']);

  setup(
    [{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
    { a: [rec('박바다')], b: [rec('박 바다')], c: [rec('박 바다')] });
  chk('띄어쓰기 차이는 경고하지 않는다', ctx.splitNameRecords('박바다'), []);
  chk('반대 방향에서도', ctx.splitNameRecords('박 바다'), []);
}

console.log('\n── 한 글자 다른 이름은 사람이 본다 ──');
{
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }],
        { a: [rec('김마루')], b: [rec('김마부')] });
  chk('한 글자 다른 이름을 찾는다',
      ctx.splitNameRecords('김마루'), [{ name: '김마부', n: 1, why: '한 글자 다름' }]);
  /* 동명이인일 수 있으므로 기계가 합치지 않는다 — 되돌릴 수 없다. */
  chk('합치지는 않는다(찾아만 준다)', /rosterMerge|합친다/.test(cut('splitNameRecords')), false);
}
{
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
        { a: [rec('박바다')], b: [rec('박 바다'), rec('박바둑')], c: [rec('박바다')] });
  chk('띄어쓰기는 빼고 한 글자 차이만',
      ctx.splitNameRecords('박바다').map(x => [x.name, x.n]), [['박바둑', 1]]);
}

console.log('\n── 남남은 끌어오지 않는다 ──');
{
  /* 경고가 흔해지면 아무도 안 읽는다. 두 글자 이상 다르면 다른 사람이다. */
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
        { a: [rec('박바다')], b: [rec('이아람')], c: [rec('박서준')] });
  chk('전혀 다른 이름은 안 센다', ctx.splitNameRecords('박바다'), []);
  chk('자기 자신은 안 센다', ctx.splitNameRecords('이아람'), []);
}
{
  setup([{ id: 'a', nQ: 3 }], { a: [rec('가'), rec('나')] });
  chk('한 글자 이름끼리는 안 묶는다', ctx.splitNameRecords('가'), []);   // 편집거리 1이지만 너무 짧다
}
{
  setup([{ id: 'a', nQ: 3 }], { a: [rec('박바다'), rec(''), rec('  ')] });
  chk('빈 이름에 안 죽는다', ctx.splitNameRecords('박바다'), []);
  chk('이름이 없으면 빈 목록', ctx.splitNameRecords(''), []);
  chk('공백만이면 빈 목록', ctx.splitNameRecords('   '), []);
}

console.log('\n── 같은 시험이 두 ID 로 있어도 한 번만 센다 ──');
{
  /* KMChC 2018 은 kmchc-2018 · hwol-2018 두 ID 로 등록돼 있고 저장 키가 같다.
     회차를 돌며 그대로 세면 한 기록이 두 번 잡혀 "2건 더 있습니다" 가 된다. */
  chk('별칭이 실제로 있다', Object.keys(ctx.COHORT_ALIAS || {}).length > 0,
      /const COHORT_ALIAS=\{'/.test(SRC));
  setup([{ id: 'kmchc-2018', nQ: 3 }, { id: 'hwol-2018', nQ: 3 }],
        { 'hwol-2018': [rec('박바다'), rec('박바둑'), rec('박바둑')] });
  chk('두 번 세지 않는다', ctx.splitNameRecords('박바다'), [{ name: '박바둑', n: 2, why: '한 글자 다름' }]);
}

console.log('\n── 성적표가 실제로 말하는가 ──');
{
  /* 함수만 있고 안 부르면 화면엔 없다. 세 자리를 확인한다. */
  chk('지난 진단 대비 화면에 꽂혀 있다', /\$\{splitNote\}\n\s*\$\{summary\}/.test(SRC), true);
  chk("'첫 진단' 화면에도 꽂혀 있다",
      /성장 추적 · 기준선'\)\}\$\{splitNote\}/.test(SRC), true);
  /* 갈라진 기록이 있는데 '첫 진단입니다' 라고 단언하면 그 문장이 틀린다. */
  chk('갈라진 기록이 있으면 단언하지 않는다',
      /\$\{splitNote\?'이 이름으로는 첫':'첫'\} 진단/.test(SRC), true);
  // 선언만 있고 안 부르면 화면엔 없다 — 부르는 자리를 센다
  chk('어느 브라우저 기준인지 밝힌다',
      (SRC.match(/\$\{historyScopeNote\(\)\}/g) || []).length, 2);
  chk('시트에서 불러오기로 안내한다',
      /시트에서 불러오기 ↓<\/b> 를 먼저 눌러/.test(SRC), true);

  // 경고가 눈에 띄어야 한다 — 회색 본문에 섞이면 안 읽힌다
  const note = cut('splitNameNote');
  chk('경고를 눈에 띄게 그린다', /background:#FBF0EA/.test(note), true);
  chk('몇 건인지 적는다', /<b>\$\{tot\}건<\/b>/.test(note), true);
  chk('무엇을 해야 하는지 적는다', /명단 관리<\/b>에서 합치세요/.test(note), true);
  chk('없으면 아무것도 안 그린다', /if\(!sp\.length\) return '';/.test(note), true);
}

console.log('\n── 이미 쌓인 이름을 한 번 다듬는다 ──');
{
  /* 규칙만 바꾸면 앞으로 저장되는 것만 합쳐진다. 지금까지 '박 바다' 으로
     쌓인 회차는 그대로 갈라져 있다. 한 번 돌면서 다듬어야 한다. */
  const fn = SRC.slice(SRC.indexOf('(function tidyNames(){'));
  const body = fn.slice(0, fn.indexOf('\n})();') + 6);
  chk('저장된 이름을 다듬는다', /var fixed=nameKey\(r\.name\);/.test(body), true);
  chk('같아진 기록을 합친다', /var sig=subSig\(r\), at=seen\[sig\];/.test(body), true);
  chk('최근 것을 남긴다', /\(\(r\.ts\|\|0\)>=\(old\.ts\|\|0\)\)\?r:old/.test(body), true);
  chk('학교·학년은 채워 둔다', /if\(!win\.school&&lose\.school\)/.test(body), true);
  chk('바뀐 것이 없으면 쓰지 않는다', /if\(changed\)\{/.test(body), true);

  /* const 는 끌어올려지지 않는다. nameKey 가 뒤에 있으면 이 정리가
     ReferenceError 로 조용히 아무것도 안 한다 — 실제로 한 번 그랬다. */
  chk('nameKey 가 먼저 선언된다',
      SRC.indexOf('const nameKey=') < SRC.indexOf('(function tidyNames(){'), true);
}

console.log('\n── 앱과 학생 화면이 같은 규칙을 쓴다 ──');
{
  const SUB = fs.readFileSync(path.join(ROOT, 'final-submit.html'), 'utf8');
  const line = re => (SRC.match(re) || [''])[0].replace(/\s+/g, ' ');
  chk('두 화면의 nameKey 가 같다',
      line(/^const nameKey=.*$/m),
      (SUB.match(/^const nameKey=.*$/m) || [''])[0].replace(/\s+/g, ' '));
  chk('교사용이 저장할 때 다듬는다', /const nm=nameKey\(_v\('nm','name'\)\)/.test(SRC), true);
  chk('학생 제출도 다듬는다', /const nm=nameKey\(document\.getElementById\('nm'\)\.value\);/.test(SUB), true);
  chk('명단 열쇠도 다듬는다', /return \[nameKey\(r\.name\)\|\|'\(이름 없음\)'/.test(SRC), true);
  chk('같은 응시 판정도 다듬는다', /function subSig\(r\)\{ return nameKey\(r\.name\)/.test(SRC), true);
  chk('시트에서 받아올 때도 다듬는다', /name:nameKey\(applyRename\(rec\.name\)\)/.test(SRC), true);
  // 시트 쪽은 이미 공백을 지우고 견주고 있었다 — 두 쪽 규칙이 같아야 한다
  chk('시트 쪽도 같은 규칙',
      /function _normName\(s\) \{ return String\(s == null \? '' : s\)\.replace\(\/\\s\+\/g, ''\)\.trim\(\); \}/
        .test(fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8')), true);
}

console.log('\n── 시트와 언제 맞췄는지 남긴다 ──');
{
  /* 시트가 진짜 원본이다. 언제 맞췄는지를 남겨야 얼마나 묵었는지 말할 수 있고,
     통합관리 화면이 오래됐을 때 스스로 맞출 수 있다. */
  const fn = cut('syncAllFromSheet');
  chk('끝나면 시각을 남긴다', /markSynced\(\);/.test(fn), true);
  chk('끝난 것을 부르는 쪽에 알린다', /if\(typeof onDone==='function'\) onDone\(/.test(fn), true);
  chk('조용히 돌 수 있다', /function syncAllFromSheet\(onDone, quiet\)/.test(fn), true);
  chk('조용할 때는 진행을 안 띄운다', /if\(!quiet\) fToast/.test(fn), true);

  /* 이제는 한 번에 받는다(action=all). 그래도 시트 쪽이 아직 옛 판이면
     회차별로 되돌아가는데, 그 길은 예전 그대로여야 한다 — 망이 끊긴 채로
     서른여덟 번을 차례로 부르면 7분 반을 붙잡는다. */
  const per = cut('syncPerExam');
  /* 한 회차도 못 받았으면 맞췄다고 할 수 없다. 그때 시각을 찍으면 망이 끊긴
     채로 '방금 맞춤' 이 되어 다음에도 안 맞춘다. */
  chk('전부 실패했으면 안 남긴다', /if\(failed<list\.length\) markSynced\(\);/.test(per), true);
  chk('연달아 실패하면 그만둔다', /if\(consec>=3 && total===0\)/.test(per), true);
  chk('그만둔 것을 말한다', /gaveUp/.test(per), true);
  chk('한 번이라도 받았으면 계속한다', /total===0/.test(per), true);
  chk('성공하면 실패 횟수를 되돌린다', /consec=0;/.test(per), true);

  const SRC2 = SRC;
  chk('통합관리가 읽을 수 있게 같은 열쇠를 쓴다',
      /const SYNC_KEY='chemistreal:final:lastsync';/.test(SRC2), true);
  chk('통합관리도 같은 열쇠를 본다',
      /const SYNC_KEY='chemistreal:final:lastsync';/.test(
        fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8')), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
