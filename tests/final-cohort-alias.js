/* ============================================================
   final.html 또래 통계 풀 병합 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   같은 시험이 두 ID 로 등록된 쌍이 있다(화올 ↔ KMChC).

     hwol-2018 ≡ kmchc-2018 · hwol-2019 ≡ kmchc-2019 · hwol-2024 ≡ kmchc-2024-1

   문항 크롭 이미지까지 바이트 단위로 같고, 문항 수·정답·복수정답·제외 문항·
   수상 컷이 모두 일치한다. 응시 기록이 두 풀로 갈리면 각 풀이 MINP(8명)를 넘지
   못해 또래 정답률·선택 분포·백분위가 아예 나오지 않으므로, 로스터 키를 한쪽으로
   모아 둔다(COHORT_ALIAS).

   여기서 지키는 것:
   - 별칭 ID 로 저장해도 대표 키 한 곳에만 쌓인다
   - 어느 ID 로 읽어도 같은 풀이 나온다
   - 예전에 별칭 키에 쌓여 있던 기록은 첫 실행에서 대표 키로 옮겨진다
   - 양쪽에 중복 저장된 응시는 한 번만 남는다
   - 짝지어진 두 시험의 채점 규칙이 실제로 같다(다르면 합치면 안 된다)

   실행:  node tests/final-cohort-alias.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'final.html'), 'utf8');

let pass = 0, fail = 0;
function chk(desc, got, exp) {
  const ok = JSON.stringify(got) === JSON.stringify(exp);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc + (ok ? '' : ' → ' + JSON.stringify(got) + ' (기대 ' + JSON.stringify(exp) + ')'));
  ok ? pass++ : fail++;
}

/* ── final.html 에서 실제 구현을 그대로 떼어 온다(구현과 테스트가 갈라지지 않게) ── */
function slice(from, to) {
  const a = src.indexOf(from);
  if (a < 0) throw new Error('찾지 못함: ' + from);
  const b = src.indexOf(to, a);
  if (b < 0) throw new Error('찾지 못함: ' + to);
  return src.slice(a, b + to.length);
}
const impl = slice("const COHORT_ALIAS=", "})();");

/* localStorage 흉내 */
function makeStore(seed) {
  const m = Object.assign({}, seed || {});
  return {
    getItem: k => (k in m ? m[k] : null),
    setItem: (k, v) => { m[k] = String(v); },
    removeItem: k => { delete m[k]; },
    _dump: () => m,
  };
}
function boot(seed) {
  const store = makeStore(seed);
  const f = new Function('localStorage', 'PFX',
    impl + '\nreturn {subs:subs, saveSubs:saveSubs, COHORT_ALIAS:COHORT_ALIAS, cohortKey:cohortKey};');
  const api = f(store, 'final:roster:');
  return { store, api };
}
const rec = (n, ts) => ({ name: 's' + n, ts, correct: 30, total: 60, wrong: 30, ans: Array.from({ length: 60 }, (_, i) => ((n * 13 + i * 7) % 4) + 1) });

/* ── 1. 별칭 → 대표 키 매핑 ── */
{
  const { api } = boot();
  chk('kmchc-2018 은 hwol-2018 풀을 쓴다', api.cohortKey('kmchc-2018'), 'hwol-2018');
  chk('kmchc-2019 은 hwol-2019 풀을 쓴다', api.cohortKey('kmchc-2019'), 'hwol-2019');
  chk('kmchc-2024-1 은 hwol-2024 풀을 쓴다', api.cohortKey('kmchc-2024-1'), 'hwol-2024');
  chk('별칭 없는 시험은 자기 키를 그대로', api.cohortKey('jmchc-1'), 'jmchc-1');
}

/* ── 2. 어느 ID 로 저장해도 한 풀에 쌓이고, 어느 ID 로도 읽힌다 ── */
{
  const { store, api } = boot();
  api.saveSubs('kmchc-2024-1', [rec(1, 100), rec(2, 200)]);
  const cur = api.subs('kmchc-2024-1'); cur.push(rec(3, 300));
  api.saveSubs('hwol-2024', cur);
  chk('kmchc ID 로 읽은 건수', api.subs('kmchc-2024-1').length, 3);
  chk('hwol ID 로 읽은 건수', api.subs('hwol-2024').length, 3);
  chk('별칭 키에는 따로 쌓이지 않음', store.getItem('final:roster:kmchc-2024-1'), null);
}

/* ── 3. 예전에 별칭 키에 쌓여 있던 기록 이관 ── */
{
  const { store, api } = boot({
    'final:roster:kmchc-2018': JSON.stringify([rec(1, 1000), rec(2, 2000)]),
    'final:roster:hwol-2018': JSON.stringify([rec(3, 3000)]),
  });
  chk('이관 후 대표 키 건수', api.subs('hwol-2018').length, 3);
  chk('이관 후 별칭 키는 사라짐', store.getItem('final:roster:kmchc-2018'), null);
  chk('시각순 정렬', api.subs('hwol-2018').map(r => r.ts), [1000, 2000, 3000]);
}

/* ── 4. 양쪽에 중복 저장된 응시는 한 번만 ── */
{
  const same = rec(9, 5000);
  const { api } = boot({
    'final:roster:kmchc-2019': JSON.stringify([same]),
    'final:roster:hwol-2019': JSON.stringify([same]),
  });
  chk('중복 응시 제거', api.subs('hwol-2019').length, 1);
}

/* ── 5. 짝지어진 두 시험의 채점 규칙이 실제로 같은가 ──
   여기가 어긋나면 풀을 합치는 것 자체가 틀린다. */
{
  const exams = JSON.parse(src.split('const FINAL_EXAMS=')[1].split(';\n')[0]);
  const byId = {}; exams.forEach(e => { byId[e.id] = e; });
  const { api } = boot();
  const accSet = (e, q) => (e.multi && e.multi[q]) ? e.multi[q] : [e.key[q - 1]];
  Object.keys(api.COHORT_ALIAS).forEach(from => {
    const to = api.COHORT_ALIAS[from], A = byId[from], B = byId[to];
    chk(from + ' · ' + to + ' 둘 다 등록되어 있다', !!(A && B), true);
    if (!A || !B) return;
    chk(from + ' 문항 수 일치', A.nQ, B.nQ);
    chk(from + ' 수상 컷 일치', A.cut, B.cut);
    chk(from + ' 제외 문항 일치', A.miss || [], B.miss || []);
    let diff = 0;
    for (let q = 1; q <= A.nQ; q++) {
      const a = accSet(A, q).slice().sort(), b = accSet(B, q).slice().sort();
      if (JSON.stringify(a) !== JSON.stringify(b)) diff++;
    }
    chk(from + ' 정답 인정 범위가 모든 문항에서 일치', diff, 0);
  });
}

console.log('\n결과: ' + pass + ' pass / ' + fail + ' fail');
process.exit(fail ? 1 : 0);
