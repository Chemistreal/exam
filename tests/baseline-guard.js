/* ============================================================
   자동 갱신이 **자기가 못 만드는 것을 지우지 못하게**
   ------------------------------------------------------------
   기준 기록(cohort/baseline.json)은 석차의 분모이고 또래 정답률의 원본이다.
   앱스크립트가 매일 새벽 시트를 읽어 이것을 갱신한다.

   같은 사고가 **두 번** 났다.

     2026-08-03 04:52  문항별 통계(q·qc)가 열 회차에서 사라짐 — main 4시간 빨간불
     2026-08-04 04:52  또. 게다가 모집단이 387명 → 225명으로 줄었다
                       (jmchc-1 46명 → 11명). 그 분모로 석차가 나가고 있었다.

   장치는 있었다 — `byHand` 깃발이 찍힌 회차는 안 건드린다. 그런데 엑셀에서
   만든 회차에 그 깃발이 안 찍혀 있었다. 사람이 기억해야 하는 깃발은 잊히고,
   잊히면 조용히 데이터가 사라진다.

   그래서 깃발 말고 **내용**을 본다. 여기서 그 규칙을 못 박는다.

   여기서 지키는 것:
   - 문항별 통계(q·qc)를 가진 회차는 덮지 않는다 — 다시 못 만드는 것이다
   - 인원이 줄어드는 갱신은 안 받는다 — 시트에 옛 응시자가 없을 뿐이다
   - 처음 만드는 회차는 그대로 만든다 (막기만 하는 장치면 쓸모가 없다)
   - 늘어나는 갱신은 그대로 받는다
   - 지금 저장소에 든 기준 기록이 **시험 목록에 있는 회차뿐**이다
     (없는 회차가 섞이면 그건 자동 갱신이 제목을 잘못 읽은 것이다)

   실행:  node tests/baseline-guard.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* 앱스크립트 한 덩어리에서 판정 함수만 오려 낸다. 브라우저도 시트도 없이
   돌려야 CI 에서 매번 돈다. */
const GS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
function cut(name) {
  const at = GS.search(new RegExp(`^function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`AppsScript-Code.gs 에서 ${name} 을 못 찾았다`);
  let depth = 0, end = -1;
  for (let j = GS.indexOf('{', at); j < GS.length; j++) {
    if (GS[j] === '{') depth++;
    else if (GS[j] === '}') { depth--; if (!depth) { end = j + 1; break; } }
  }
  return GS.slice(at, end);
}
const ctx = { console };
vm.createContext(ctx);
vm.runInContext(cut('_baselineKeepWhy_'), ctx);
const why = (old, n, flag) => ctx._baselineKeepWhy_(old, n, flag);

console.log('── 못 만드는 것은 안 지운다 ──');
{
  /* 실제로 지워진 모양 그대로. jmchc-1 은 엑셀에서 온 46명이었고 문항별
     통계를 갖고 있었는데, 시트에서 센 11명으로 통째로 덮였다. */
  const jm1 = { n: 46, hist: { 30: 46 }, q: [[1, 0, 0, 0]], qc: [1] };
  chk('문항별 통계가 있으면 안 덮는다', why(jm1, 11, 0), '문항별통계');
  chk('인원이 늘어도 안 덮는다(통계를 잃는다)', why(jm1, 99, 0), '문항별통계');
  chk('qc 만 있어도 안 덮는다', why({ n: 5, qc: [1] }, 9, 0), '문항별통계');
}

console.log('\n── 인원이 줄어드는 갱신은 안 받는다 ──');
{
  const plain = { n: 42, hist: { 30: 42 }, from: 'sheet' };
  chk('42명이 12명이 되면 막는다', why(plain, 12, 0), '인원감소 42→12');
  chk('같은 인원이면 지나간다', why(plain, 42, 0), '');
  chk('늘어나면 지나간다', why(plain, 43, 0), '');
}

console.log('\n── 막기만 하면 쓸모가 없다 ──');
{
  chk('처음 만드는 회차는 그대로 만든다', why(null, 9, 0), '');
  chk('없던 것은 undefined 여도 만든다', why(undefined, 9, 0), '');
  chk('손입력 깃발은 그대로 살아 있다', why({ n: 3 }, 99, 1), '손입력');
}

console.log('\n── 지금 저장소에 든 기준 기록 ──');
{
  const BASE = JSON.parse(fs.readFileSync(path.join(ROOT, 'cohort', 'baseline.json'), 'utf8')).exams;
  const exams = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
  const list = Array.isArray(exams) ? exams : (exams.exams || []);
  const ids = new Set(list.map(e => e.id));
  /* 자동 갱신이 제목을 잘못 읽으면 'j0' 같은 유령 회차가 생긴다. 실제로
     생겼고, 시험 목록에 없으니 화면에서는 안 보이는데 파일에는 남았다. */
  chk('시험 목록에 없는 회차가 섞여 있지 않다',
      Object.keys(BASE).filter(id => !ids.has(id)), []);
  /* 문항별 통계가 한 회차라도 사라지면 여기서 걸린다. 지난 두 번의 사고가
     정확히 이 모양이었다. */
  chk('문항별 통계가 빠진 회차가 없다',
      Object.keys(BASE).filter(id => !BASE[id].q || !BASE[id].qc), []);
  const total = Object.keys(BASE).reduce((a, k) => a + BASE[k].n, 0);
  console.log('  회차 ' + Object.keys(BASE).length + ' · 인원 ' + total);
  /* 줄어들면 걸린다. 늘리는 것은 사람이 이 줄을 같이 고치면 된다 — 그때는
     '왜 늘었나' 가 커밋에 남는다. */
  chk('기준 인원이 387명 아래로 내려가지 않았다', total >= 387, true);
}

console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
process.exit(fail ? 1 : 0);
