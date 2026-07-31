/* ============================================================
   갈라진 이름표 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   성적표는 이름이 **정확히 같은** 기록만 한 학생으로 본다. final.html 안에서
   아홉 군데가 같은 규칙을 쓴다:

       subs(e.id).filter(r => r.name.trim() === nm && r.ans.length === e.nQ)

   그래서 '박 하람' 처럼 공백 하나, 글자 하나가 어긋난 기록은 조용히 빠진다.
   화면은 "진단 6회 누적" 이라고 **단언하고**, 첫 회차만 갈라져 있으면
   학부모에게 나가는 종이에 "첫 진단입니다" 라고 적힌다. 읽는 쪽에는 빠졌다는
   신호가 어디에도 없다 — 선생님이 "3·4회 봤다던데" 하고 되물어야만 드러난다.

   고칠 수 있는 것은 합치는 일(명단 관리)이지만, **모르면 합칠 수도 없다.**
   그래서 성적표가 먼저 말한다.

   여기서 지키는 것:
   - 띄어쓰기만 다른 이름을 찾아낸다
   - 한 글자 다른 이름을 찾아낸다
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
  cut('editDist'),
  'function subs(id){ return STORE[cohortKey(id)] || []; }',
  cut('splitNameRecords'),
  'Object.assign(globalThis,{splitNameRecords, cohortKey, COHORT_ALIAS});',
].join('\n'), ctx);

const setup = (exams, store) => { ctx.FINAL_EXAMS = exams; ctx.STORE = store; };
const rec = name => ({ name, ans: [1, 2, 3], correct: 1, total: 3 });

console.log('── 갈라진 이름을 찾아낸다 ──');
{
  setup(
    [{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
    { a: [rec('박하람')], b: [rec('박 하람')], c: [rec('박 하람')] });
  chk('띄어쓰기만 다른 기록을 센다',
      ctx.splitNameRecords('박하람'), [{ name: '박 하람', n: 2, why: '띄어쓰기만 다름' }]);
  chk('반대 방향에서도 찾는다',
      ctx.splitNameRecords('박 하람'), [{ name: '박하람', n: 1, why: '띄어쓰기만 다름' }]);
}
{
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }],
        { a: [rec('김지성')], b: [rec('김지선')] });
  chk('한 글자 다른 이름을 찾는다',
      ctx.splitNameRecords('김지성'), [{ name: '김지선', n: 1, why: '한 글자 다름' }]);
}
{
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
        { a: [rec('박하람')], b: [rec('박 하람'), rec('박하늘')], c: [rec('박하람')] });
  const got = ctx.splitNameRecords('박하람');
  chk('여러 표기를 많은 순으로', got.map(x => [x.name, x.n]), [['박 하람', 1], ['박하늘', 1]]);
}

console.log('\n── 남남은 끌어오지 않는다 ──');
{
  /* 경고가 흔해지면 아무도 안 읽는다. 두 글자 이상 다르면 다른 사람이다. */
  setup([{ id: 'a', nQ: 3 }, { id: 'b', nQ: 3 }, { id: 'c', nQ: 3 }],
        { a: [rec('박하람')], b: [rec('이도현')], c: [rec('박서준')] });
  chk('전혀 다른 이름은 안 센다', ctx.splitNameRecords('박하람'), []);
  chk('자기 자신은 안 센다', ctx.splitNameRecords('이도현'), []);
}
{
  setup([{ id: 'a', nQ: 3 }], { a: [rec('가'), rec('나')] });
  chk('한 글자 이름끼리는 안 묶는다', ctx.splitNameRecords('가'), []);   // 편집거리 1이지만 너무 짧다
}
{
  setup([{ id: 'a', nQ: 3 }], { a: [rec('박하람'), rec(''), rec('  ')] });
  chk('빈 이름에 안 죽는다', ctx.splitNameRecords('박하람'), []);
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
        { 'hwol-2018': [rec('박하람'), rec('박 하람')] });
  chk('두 번 세지 않는다', ctx.splitNameRecords('박하람'), [{ name: '박 하람', n: 1, why: '띄어쓰기만 다름' }]);
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

console.log('\n── 시트와 언제 맞췄는지 남긴다 ──');
{
  /* 시트가 진짜 원본이다. 언제 맞췄는지를 남겨야 얼마나 묵었는지 말할 수 있고,
     통합관리 화면이 오래됐을 때 스스로 맞출 수 있다. */
  const fn = cut('syncAllFromSheet');
  chk('끝나면 시각을 남긴다', /markSynced\(\);/.test(fn), true);
  /* 한 회차도 못 받았으면 맞췄다고 할 수 없다. 그때 시각을 찍으면 망이 끊긴
     채로 '방금 맞춤' 이 되어 다음에도 안 맞춘다. */
  chk('전부 실패했으면 안 남긴다', /if\(failed<list\.length\) markSynced\(\);/.test(fn), true);
  chk('끝난 것을 부르는 쪽에 알린다', /if\(typeof onDone==='function'\) onDone\(/.test(fn), true);
  chk('조용히 돌 수 있다', /function syncAllFromSheet\(onDone, quiet\)/.test(fn), true);
  chk('조용할 때는 진행을 안 띄운다', /if\(!quiet\) fToast/.test(fn), true);

  /* 한 번에 최대 12초를 기다린다. 망이 끊긴 채로 서른여덟 번을 차례로 부르면
     7분 반을 붙잡는다 — 자동으로 도는 자리에서는 그동안 갇힌다. */
  chk('연달아 실패하면 그만둔다', /if\(consec>=3 && total===0\)/.test(fn), true);
  chk('그만둔 것을 말한다', /gaveUp/.test(fn), true);
  chk('한 번이라도 받았으면 계속한다', /total===0/.test(fn), true);
  chk('성공하면 실패 횟수를 되돌린다', /consec=0;/.test(fn), true);

  const SRC2 = SRC;
  chk('통합관리가 읽을 수 있게 같은 열쇠를 쓴다',
      /const SYNC_KEY='chemistreal:final:lastsync';/.test(SRC2), true);
  chk('통합관리도 같은 열쇠를 본다',
      /const SYNC_KEY='chemistreal:final:lastsync';/.test(
        fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8')), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
