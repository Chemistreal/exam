/* ============================================================
   연도누적 총석차 · 당해년도 반석차 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   석차가 하나뿐이면 그 숫자가 무엇을 뜻하는지 읽는 쪽이 알 수 없다.
   「석차 44/47」의 47명은 몇 해에 걸쳐 이 회차를 본 사람 전부다. 학부모가
   알고 싶은 것은 대개 "지금 같이 배우는 아이들 안에서 몇 등이냐" 인데,
   그 숫자는 어디에도 없었다.

   그래서 둘을 나란히 적는다.
       연도누적 총석차  — 이 회차를 여태 본 사람 전부(기준 기록 포함)
       2026년 반석차    — 올해 채점해 넣은 학생만

   여기서 지키는 것:
   - 두 모집단이 서로 다르다(올해 것이 누적보다 작거나 같다)
   - 기준 기록(지난 회차 응시자)은 반석차에 들어가지 않는다
   - 연도를 알 수 없는 옛 기록은 올해로 세지 않는다
   - 같은 학생을 두 번 세지 않는다
   - 올해 기록이 없으면 반석차를 지어내지 않는다
   - 시트(문자)와 앱이 같은 규칙으로 센다

   실행:  node tests/rank-year.js
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
function cutFn(src, name) {
  const at = src.search(new RegExp(`^function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`${name} 을 못 찾았다`);
  let d = 0;
  for (let j = src.indexOf('{', at); j < src.length; j++) {
    if (src[j] === '{') d++;
    else if (src[j] === '}') { d--; if (!d) return src.slice(at, j + 1); }
  }
  throw new Error(`${name} 의 끝을 못 찾았다`);
}

const YEAR = new Date().getFullYear();
const ctx = { console, BASELINE: null, MINP: 1, Date };
vm.createContext(ctx);
vm.runInContext([
  'var CUR_YEAR=' + YEAR + ';',
  cutFn(SRC, 'rankIn'), cutFn(SRC, 'rankPoolYear'),
  cutFn(SRC, 'rankPool'), cutFn(SRC, 'baselineTotals'),
  /* 시트가 대답한 '지금 인원'. 링크에 실린 낡은 숫자를 갈아 끼우는 자리라
     여기서도 실물을 넣는다 — 흉내로 두면 갈아 끼우는 규칙을 못 잰다. */
  'var LIVE_POOL=null;', cutFn(SRC, 'liveTotals'),
  'var COHORT_ALIAS={}; function cohortKey(id){return id;}',
].join('\n'), ctx);

const ex = { id: 'x-1', nQ: 60 };

console.log('── 두 모집단은 서로 다르다 ──');
{
  /* 기준 기록 40명 + 이 브라우저 기록 5명(그중 올해 3명). */
  ctx.BASELINE = { 'x-1': { n: 40, hist: { 30: 20, 40: 20 } } };
  const cs = { N: 5, totals: [55, 50, 45, 20, 10], yearTotals: [55, 50, 45] };
  const rp = ctx.rankPool(ex, cs), ry = ctx.rankPoolYear(ex, cs);
  chk('누적은 기준 기록까지 센다', rp.N, 45);
  chk('반석차는 올해 것만 센다', ry.N, 3);
  chk('올해 모집단이 더 작다', ry.N < rp.N, true);
  chk('50점이면 누적 2등', ctx.rankIn(rp.pool, 50), 2);
  chk('50점이면 올해 2등', ctx.rankIn(ry.pool, 50), 2);
  chk('45점이면 누적 3등 · 올해 3등',
      [ctx.rankIn(rp.pool, 45), ctx.rankIn(ry.pool, 45)], [3, 3]);
  // 작년 학생이 섞이면 등수가 달라진다 — 그게 두 줄을 적는 이유다
  chk('10점이면 누적 45등 · 올해 4등',
      [ctx.rankIn(rp.pool, 10), ctx.rankIn(ry.pool, 10)], [45, 4]);
  chk('반석차 라벨에 쓸 연도', ry.year, YEAR);
}

console.log('\n── 기준 기록은 반석차에 안 들어간다 ──');
{
  ctx.BASELINE = { 'x-1': { n: 40, hist: { 59: 40 } } };   // 지난 회차 만점자 40명
  const cs = { N: 1, totals: [30], yearTotals: [30] };
  const ry = ctx.rankPoolYear(ex, cs);
  chk('올해 한 명뿐', ry.N, 1);
  chk('올해는 1등', ctx.rankIn(ry.pool, 30), 1);
  chk('누적으로는 41등', ctx.rankIn(ctx.rankPool(ex, cs).pool, 30), 41);
}

console.log('\n── 없는 것을 지어내지 않는다 ──');
{
  chk('올해 기록이 없으면 안 내놓는다', ctx.rankPoolYear(ex, { N: 3, totals: [1, 2, 3] }).ready, false);
  chk('빈 통계에도 안 죽는다', ctx.rankPoolYear(ex, null).ready, false);
  chk('빈 배열도 준비되지 않은 것', ctx.rankPoolYear(ex, { yearTotals: [] }).ready, false);
}

console.log('\n── 올해 기록을 고르는 규칙 ──');
{
  /* cohortStats 가 ts 로 연도를 가른다. 코드를 그대로 오려 낼 수 없어
     같은 식을 여기서 돌린다 — 소스에 그 식이 살아 있는지도 함께 본다. */
  chk('저장 시각으로 연도를 가른다',
      /d\.getFullYear\(\)===CUR_YEAR/.test(SRC), true);
  chk('시각이 없는 기록은 뺀다', /if\(!r\.ts\) return false/.test(SRC), true);
  chk('올해 기록을 통계에 실어 보낸다', /yearTotals/.test(SRC), true);
  chk('기준 기록을 반석차에 섞지 않는다',
      /function rankPoolYear[\s\S]{0,300}baselineTotals/.test(SRC), false);

  const pick = arr => arr.filter(r => { if (!r.ts) return false;
    const d = new Date(r.ts); return !isNaN(d) && d.getFullYear() === YEAR; }).map(r => r.correct);
  chk('올해 것만 고른다',
      pick([{ ts: Date.UTC(YEAR, 5, 1), correct: 50 },
            { ts: Date.UTC(YEAR - 1, 5, 1), correct: 40 },
            { ts: 0, correct: 30 },
            { correct: 20 }]),
      [50]);
}

console.log('\n── 같은 학생을 두 번 세지 않는다 ──');
{
  /* totals 는 latestPerStudent 를 지난 배열에서 나온다. 같은 근원에서
     yearTotals 도 나오므로, 중복 제거가 한쪽만 걸리는 일이 없어야 한다. */
  const i1 = SRC.indexOf('const totals=arr.map(r=>r.correct);');
  const i2 = SRC.indexOf('const yearTotals=arr.filter');
  chk('둘 다 같은 배열에서 나온다', i1 >= 0 && i2 > i1 && i2 - i1 < 400, true);
  chk('그 배열은 학생별 최신 1건이다',
      /latestPerStudent\(subs\(exam\.id\)/.test(SRC), true);
}

console.log('\n── 링크로 받은 것이면 그때 그 해를 쓴다 ──');
{
  /* 선생님 화면에는 반석차가 나오는데 보내 준 링크에는 안 나왔다. 점수 분포는
     실었지만 **몇 해 것인지**를 안 실어서, 받는 쪽이 올해 것을 골라낼 수가
     없었다. 이제 링크가 연도를 함께 나른다. */
  chk('링크에 적힌 해를 그대로 쓴다',
      ctx.rankPoolYear(ex, { yearTotals: [50, 40, 30], yearOf: 2025 }).year, 2025);
  chk('해가 없으면 올해로 본다',
      ctx.rankPoolYear(ex, { yearTotals: [50, 40, 30] }).year, YEAR);
  // 혼자면 1/1 이 되는데 그건 등수가 아니라 아직 아무도 없다는 뜻이다(시트도 같다)
  chk('올해 한 명뿐이면 등수로 안 친다',
      ctx.rankPoolYear(ex, { yearTotals: [30], yearOf: YEAR }).ready, false);

  chk('링크가 올해 분포를 함께 싣는다', /putHist\(cs\.yearTotals\)/.test(SRC), true);
  chk('링크가 연도도 싣는다', /cs\.yearOf\|\|CUR_YEAR\)-2000/.test(SRC), true);
  chk('푸는 쪽도 연도를 읽는다', /yearOf=2000\+r\.get\(8\)/.test(SRC), true);
  // 이미 학부모에게 나간 링크가 빈 성적표가 되면 안 된다
  chk('예전 판 링크를 계속 읽는다', /b\[0\]!==2 && b\[0\]!==CS_VER/.test(SRC), true);
  /* 라벨을 이 브라우저의 올해로 붙이면, 해가 바뀐 뒤 학부모가 링크를 열었을 때
     선생님 화면과 다른 해가 적힌다. 링크가 나른 해로만 적는다. */
  chk('라벨에 이 브라우저의 올해를 쓰지 않는다',
      /CUR_YEAR[^\n]{0,16}년 반석차/.test(SRC.replace(/\/\*[\s\S]*?\*\//g, '')), false);
}

console.log('\n── 화면·인쇄·Word 가 같은 말을 한다 ──');
{
  ['연도누적 총석차', '년 반석차'].forEach(w => {
    const n = (SRC.match(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    chk(`'${w}' 가 여러 화면에 쓰인다`, n >= 3, true);
  });
  chk('옛 라벨 "석차"만 남은 곳이 없다',
      /<span>석차<\/span>/.test(SRC), false);
}

console.log('\n── 시트 문자도 같은 규칙이다 ──');
{
  const gctx = { console, Date };
  vm.createContext(gctx);
  vm.runInContext([cutFn(GAS, '_yearOf'), cutFn(GAS, '_yearRankLine'), cutFn(GAS, '_rankPct')].join('\n'), gctx);

  chk('날짜에서 연도를 읽는다', gctx._yearOf(new Date(2026, 3, 1)), 2026);
  chk('없으면 0', [gctx._yearOf(null), gctx._yearOf(0), gctx._yearOf('')], [0, 0, 0]);
  chk('말이 안 되는 해는 0', gctx._yearOf(new Date(1899, 0, 1)), 0);

  chk('반석차 줄을 적는다', gctx._yearRankLine(2026, { rank: 3, n: 12 }), '· 2026년 반석차 3/12\n');
  // 혼자면 1/1 이 되는데, 그건 등수가 아니라 아직 아무도 없다는 뜻이다
  chk('혼자일 때는 적지 않는다', gctx._yearRankLine(2026, { rank: 1, n: 1 }), '');
  chk('연도를 모르면 적지 않는다', gctx._yearRankLine(0, { rank: 1, n: 9 }), '');
  chk('등수가 없으면 적지 않는다', gctx._yearRankLine(2026, null), '');

  // 문자 본문에 실제로 꽂혀 있는지 — 함수만 있고 안 부르면 문자엔 없다
  chk('문자에 반석차 줄이 들어간다', /\+ _yearRankLine\(year, yrp\)/.test(GAS), true);
  chk('누적 쪽 이름도 바뀌었다', /연도누적 총석차 ' \+ rank/.test(GAS), true);
  chk('연도별 코호트를 만든다', /var byYear = \{\}/.test(GAS), true);
  chk('기준분포를 연도 코호트에 넣지 않는다',
      /var byYear = \{\};[\s\S]{0,400}baseTotals/.test(GAS), false);
  chk('행마다 그 행의 해로 센다', /var yr = _yearOf\(ts\(ri\)\)/.test(GAS), true);
}

/* ── 공유 링크의 인원이 굳지 않는다 ──────────────────────────────────
   링크에 실린 점수 분포는 **링크를 지은 순간**의 것이다. 뒤에 채점한 학생이
   늘어도 학부모 화면의 분모는 그대로였다 — "총석차 1/5" 가 다섯 명인 채로
   굳는다. 시트에 지금 몇 명인지 물어 그 숫자로 바꾼다. */
console.log('\n── 공유 링크가 지금 인원을 본다 ──');
{
  const cs = { totals: [50, 40, 30] };              // 링크에 실린 그때의 셋
  ctx.BASELINE = null; ctx.LIVE_POOL = null;
  chk('시트가 없으면 링크에 실린 것을 쓴다', ctx.rankPool(ex, cs).N, 3);

  /* 같은 사람들을 세는 두 벌이라 **더하지 않고 갈아 끼운다.** 더하면 한
     사람이 두 번 세어져 분모가 부풀고 등수가 뒤로 밀린다. */
  ctx.LIVE_POOL = { id: 'x-1', hist: { 50: 1, 40: 1, 30: 1, 20: 3 }, n: 6 };
  const live = ctx.rankPool(ex, cs);
  chk('시트가 대답하면 그 숫자로', live.N, 6);
  chk('더하지 않고 갈아 끼운다', live.N === 3 + 6, false);
  chk('갈아 끼웠다고 표시한다', live.live, true);
  /* 등수도 따라 움직여야 한다 — 분모만 늘고 등수가 그대로면 더 이상하다. */
  chk('등수도 새 모집단에서', ctx.rankIn(live.pool, 40), 2);

  /* 다른 회차 것이 남아 있으면 남의 인원으로 등수를 매기게 된다. */
  ctx.LIVE_POOL = { id: '다른회차', hist: { 10: 9 }, n: 9 };
  chk('회차가 다르면 안 쓴다', ctx.rankPool(ex, cs).N, 3);

  /* 기준 기록(옛 엑셀 응시자)과는 겹치지 않는 사람들이라 그대로 더한다. */
  ctx.BASELINE = { 'x-1': { hist: { 55: 2 } } };
  ctx.LIVE_POOL = { id: 'x-1', hist: { 50: 1, 40: 1 }, n: 2 };
  chk('기준 기록에는 더한다', ctx.rankPool(ex, cs).N, 4);

  ctx.LIVE_POOL = null; ctx.BASELINE = null;
  chk('빈 대답은 안 쓴다', ctx.rankPool(ex, cs).N, 3);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
