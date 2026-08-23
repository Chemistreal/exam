/* ============================================================
   **즉시 재도전 10제가 정말 「다른 문항」 열 개인가** — 순수 node
   ------------------------------------------------------------
   규칙은 다섯 줄이다.
     ① 방금 틀린 문항의 **개념**만 모은다
     ② 그 개념의 **다른 문항**을 고른다
     ③ 정답률 20~60% 를 먼저(너무 쉬운 것도, 아무도 못 푸는 것도 아니게)
     ④ 한 영역에 몰리지 않게 나눈다
     ⑤ **방금 푼 문항은 절대 다시 내지 않는다** — 그건 재도전이 아니라 답 외우기다

   ⑤ 가 두 번 깨졌다.

     · 처음엔 srcmap 으로만 「방금 푼 것」을 셌다. srcmap 이 없는 회차
       (기출동형·화올 등 exams.json 소속)는 제 문항이 풀에 **그대로** 들어
       있어서, 몇 분 전에 틀린 그 문항이 같은 정답키로 63~99% 다시 나왔다.
     · 그것을 고치려 제 회차를 통째로 빼자 이번엔 **문항이 모자랐다.**
       오답이 한 영역에 몰리면 그 영역 문항이 자기 회차에만 있는 일이 잦아,
       한 영역 몰빵 677가지 중 55.6% 가 열 문항을 못 채웠고 최소 0제였다 —
       「같은 개념의 다른 문항을 못 찾았습니다」. 오답이 몰린 학생일수록
       재도전이 더 필요한데 **바로 그 학생부터 못 받았다.**

   그래서 못 채우면 큰 영역(RXMAP)으로, 그래도 모자라면 제 회차의 «맞혔던»
   문항까지 넓힌다. 넓히더라도 ⑤ 는 안 깬다. 그 둘을 여기서 동시에 센다.

   실행:  node tests/retry-compose.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const POOL = JSON.parse(fs.readFileSync(path.join(ROOT, 'retry-pool.json'), 'utf8')).q;
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));

let pass = 0, fail = 0;
function chk(desc, ok, extra) {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc + (extra ? '  ' + extra : ''));
  ok ? pass++ : fail++;
}

function cut(from, to) {
  const a = html.indexOf(from);
  if (a < 0) throw new Error('없다: ' + from);
  return html.slice(a, html.indexOf(to, a) + to.length);
}
const compose = new Function(
  cut('const RXMAP=', '\n') + '\n' + cut('const RX={', '\n};') + '\n'
  + cut('function retryBand', '\n}') + '\n'
  + cut('function retryCompose', '\n  return take.length?take:null;\n}')
  + ';return retryCompose;')();

/* 되풀이 가능한 난수 — Math.random 을 쓰면 실패가 재현이 안 된다. */
let _s = 20260821;
const rnd = () => ((_s = (_s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);

const withArea = EXAMS.filter(e => e.area && e.area.some(Boolean));
console.log('── 회차 ' + withArea.length + '개 · 풀 ' + POOL.length + '문항 ──');

/* ── ① 오답이 한 영역에 몰린 경우 (가장 아픈 경우) ── */
console.log('\n── 오답이 한 영역에 몰릴 때 ──');
{
  let tot = 0, short = 0, nul = 0, self = 0, min = 99;
  for (const e of withArea) {
    for (const a of [...new Set(e.area.filter(Boolean))]) {
      const wrong = [];
      e.area.forEach((x, i) => { if (x === a) wrong.push(i + 1); });
      if (!wrong.length) continue;
      tot++;
      const t = compose(e, wrong.slice(0, 8), POOL.slice(), 10);
      const k = t ? t.length : 0;
      if (!t) nul++;
      if (k < 10) short++;
      if (k < min) min = k;
      if (t && t.some(x => x.e === e.id && wrong.indexOf(x.q) >= 0)) self++;
    }
  }
  chk('열 문항을 다 채운다', short === 0, tot + '가지 중 미달 ' + short + '건 · 최소 ' + min + '제');
  chk('«못 찾았습니다» 로 끝나지 않는다', nul === 0, nul + '건');
  chk('방금 틀린 문항은 하나도 안 나온다', self === 0, self + '건');
}

/* ── ② 오답이 흩어진 보통 경우 ── */
console.log('\n── 오답이 여러 영역에 흩어질 때 ──');
{
  let tot = 0, short = 0, self = 0, dupe = 0;
  for (const e of withArea) {
    const nQ = e.nQ || (e.key ? e.key.length : 0);
    for (let trial = 0; trial < 40; trial++) {
      const wrong = [];
      for (let q = 1; q <= nQ; q++) if (rnd() < 0.22) wrong.push(q);
      if (!wrong.length) continue;
      tot++;
      const t = compose(e, wrong, POOL.slice(), 10);
      if (!t || t.length < 10) { short++; continue; }
      if (t.some(x => x.e === e.id && wrong.indexOf(x.q) >= 0)) self++;
      const seen = {};
      if (t.some(x => { const k = x.e + '#' + x.q; if (seen[k]) return true; seen[k] = 1; return false; })) dupe++;
    }
  }
  chk('열 문항을 다 채운다', short === 0, tot + '번 중 미달 ' + short + '건');
  chk('방금 틀린 문항은 하나도 안 나온다', self === 0, self + '건');
  chk('같은 문항이 두 번 안 들어간다', dupe === 0, dupe + '건');
}

/* ── ③ 복수정답 문항은 애초에 풀에 없다 ── */
console.log('\n── 복수정답 문항 ──');
{
  const bad = [];
  for (const e of EXAMS) {
    for (const q of Object.keys(e.multi || {})) {
      if (POOL.some(x => x.e === e.id && x.q === +q)) bad.push(e.id + ' ' + q + '번');
    }
  }
  chk('풀에 복수정답 문항이 없다', bad.length === 0, bad.slice(0, 5).join(' · ') || '없음');
  /* 봉투는 정답을 하나만 싣는다 — 인정되는 답을 고르고도 오답이 되면 안 된다. */
  chk('풀의 정답은 모두 한 자리 숫자다',
    POOL.every(x => Number.isInteger(x.k) && x.k >= 1 && x.k <= 5), '');
}

/* ── ④ 정답률 20~60% 를 먼저 준다 ── */
console.log('\n── 고르는 순서 ──');
{
  const e = withArea.find(x => (x.rate || []).some(r => r));
  const wrong = [];
  e.area.forEach((x, i) => { if (x) wrong.push(i + 1); });
  const t = compose(e, wrong.slice(0, 6), POOL.slice(), 10) || [];
  const rated = t.filter(x => typeof x.r === 'number');
  const band0 = rated.filter(x => x.r >= 20 && x.r <= 60).length;
  chk('정답률이 있는 것 중 대부분이 20~60% 다',
    !rated.length || band0 >= Math.ceil(rated.length * 0.6),
    band0 + ' / ' + rated.length + ' (' + e.id + ')');
}

console.log('\n' + (fail ? `실패 ${fail}건 / 통과 ${pass}건`
  : `통과 ${pass}건 — 열 문항이 늘 채워지고, 방금 푼 문항은 안 나온다.`));
process.exit(fail ? 1 : 0);
