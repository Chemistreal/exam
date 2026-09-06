/* ============================================================
   final.html 또래 통계 풀 병합 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   같은 시험이 두 ID 로 등록돼 있었다(화올 ↔ KMChC). 화올은 KMChC 의 옛 이름이다.

     hwol-2018 ≡ kmchc-2018 · hwol-2019 ≡ kmchc-2019 · hwol-2024 ≡ kmchc-2024-1

   문항 크롭 이미지까지 바이트 단위로 같고, 문항 수·정답·복수정답·제외 문항·
   수상 컷이 모두 일치했다. 그래서 시험 목록에서는 한쪽만 남겼다. 남은 문제는
   이미 브라우저에 쌓여 있는 응시 기록인데, 두 풀로 갈려 있으면 각 풀이
   MINP(8명)를 넘지 못해 또래 정답률·선택 분포·백분위가 아예 나오지 않는다.
   COHORT_ALIAS 가 옛 키를 살아 있는 키로 옮겨 준다.

   여기서 지키는 것:
   - 별칭 ID 로 저장해도 대표 키 한 곳에만 쌓인다
   - 어느 ID 로 읽어도 같은 풀이 나온다
   - 예전에 별칭 키에 쌓여 있던 기록은 첫 실행에서 대표 키로 옮겨진다
   - 양쪽에 중복 저장된 응시는 한 번만 남는다
   - 없앤 쪽 ID 는 목록에서 빠졌고, 그 ID 로 집필한 동형문제는 남긴 시험의
     문제풀에 들어가 계속 쓰인다(DH_SETS)

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

/* ── 5. 병합된 쪽 ID 의 뒤처리 ──
   두 ID 가 같은 시험이라는 것이 확인된 뒤, 시험 목록에서는 한쪽을 없앴다.
   그래서 COHORT_ALIAS 는 이제 "두 목록 사이를 잇는 다리"가 아니라
   "예전 브라우저에 남아 있는 옛 키를 살아 있는 키로 옮기는 이삿짐"이다.
   지켜야 할 것은 두 가지다.
     - 없앤 쪽 ID 는 정말로 목록에서 빠졌고, 남긴 쪽은 그대로 있다
     - 없앤 쪽 ID 로 집필해 둔 동형문제는 버려지지 않고 남긴 시험의
       문제풀(DH_SETS)에 들어가 있다 — 틀린 문항마다 연습 문제를 두 벌 받는다 */
{
  const exams = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'exams.json'), 'utf8'));
  const byId = {}; exams.forEach(e => { byId[e.id] = e; });
  const { api } = boot();
  /* DH_SETS 는 자바스크립트라 **끝 쉼표**가 허용된다. 그것을 그대로 JSON 에
     넘기면 «Expected double-quoted property name» 로 죽는데, 그 말은 마치
     화면이 깨진 것처럼 들린다 — 실제로는 이 검사의 읽는 법이 좁았을 뿐이다.
     따옴표를 바꾼 뒤 끝 쉼표를 걷어 낸다. */
  const DH_SETS = JSON.parse(
    (src.split('const DH_SETS=')[1].split('};')[0].replace(/'/g, '"') + '}')
      .replace(/,(\s*[}\]])/g, '$1'));

  Object.keys(api.COHORT_ALIAS).forEach(from => {
    const to = api.COHORT_ALIAS[from];
    chk(from + ' 은 시험 목록에서 빠졌다', !!byId[from], false);
    chk(to + ' 은 시험 목록에 남아 있다', !!byId[to], true);
    const set = DH_SETS[to] || [];
    chk(to + ' 문제풀에 ' + from + ' 동형문제가 들어 있다', set.indexOf(from) >= 0, true);
    chk(to + ' 문제풀에 자기 동형문제도 들어 있다', set.indexOf(to) >= 0, true);
  });

  /* 문제풀에 담긴 파일이 모두 있고, 시험의 모든 문항을 빠짐없이 덮는가.
     한 벌이라도 문항이 모자라면 그 문항만 연습 문제가 한 개로 줄어든다. */
  Object.keys(DH_SETS).forEach(to => {
    const nQ = byId[to] ? byId[to].nQ : 0;
    chk(to + ' 은 등록된 시험이다', nQ > 0, true);
    DH_SETS[to].forEach(fileId => {
      const p = path.join(__dirname, '..', 'donghyung', fileId + '.json');
      if (!fs.existsSync(p)) { chk(fileId + '.json 존재', false, true); return; }
      const doc = JSON.parse(fs.readFileSync(p, 'utf8'));
      const qs = doc.questions || doc;
      const missing = [];
      for (let q = 1; q <= nQ; q++) if (!qs[String(q)]) missing.push(q);
      chk(fileId + '.json 이 1~' + nQ + '번을 모두 덮는다', missing, []);
    });
  });
}

console.log('\n결과: ' + pass + ' pass / ' + fail + ' fail');
process.exit(fail ? 1 : 0);
