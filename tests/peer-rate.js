/* ============================================================
   또래 정답률 모집단 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   석차는 기준 기록(cohort/baseline.json)을 모집단으로 쓰는데 **정답률은
   안 쓰고 있었다.** 그래서 성적표에 "석차 12/57" 바로 옆에 "또래 정답률
   33%"가 나란히 찍혔는데, 뒤엣것은 3명이 만든 33% 였다. 같은 또래를
   말하면서 한쪽은 57명, 한쪽은 3명.

   여기서 지키는 것:
   - 정답률·선택 분포가 기준 기록 + 이번 누적 응시를 **합친 수**로 나온다
   - 그 인원이 석차의 인원과 같다(두 숫자가 서로 다른 말을 하면 안 된다)
   - 정답률은 앱의 채점 규칙(복수정답·전원정답)과 어긋나지 않는다
   - 공유 링크에는 **이 브라우저에서 채점한 사람만** 실린다(주소가 안 길어진다)
     — 받는 쪽이 자기 baseline.json 으로 같은 결과를 만든다
   - 기준 기록이 없는 시험은 예전 그대로 이 브라우저 기록만 쓴다
   - 저장된 문항별 집계가 앞뒤가 맞는다(합계 = 응시 인원)

   실행:  node tests/peer-rate.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
const BASE = JSON.parse(fs.readFileSync(path.join(ROOT, 'cohort', 'baseline.json'), 'utf8')).exams;

/* final.html 은 브라우저용 한 덩어리라 통째로 못 돌린다. 통계에 쓰이는 함수만
   이름으로 오려 낸다 — 원본이 바뀌면 여기서 못 찾아 바로 빨간불이 된다. */
function cut(name, kind) {
  const head = (kind === 'const' || kind === 'block') ? new RegExp(`^const ${name}=`, 'm')
                                : new RegExp(`^function ${name}\\(`, 'm');
  const at = SRC.search(head);
  if (at < 0) throw new Error(`final.html 에서 ${name} 을 못 찾았다`);
  let i = SRC.indexOf('{', at), depth = 0, end = -1;
  if (kind === 'const') { end = SRC.indexOf('\n', at); return SRC.slice(at, end); }
  for (let j = i; j < SRC.length; j++) {
    if (SRC[j] === '{') depth++;
    else if (SRC[j] === '}') { depth--; if (!depth) { end = j + 1; break; } }
  }
  return SRC.slice(at, end);
}

const ctx = { BASELINE: null, console, Buffer };
vm.createContext(ctx);
vm.runInContext([
  cut('accSet', 'const'), cut('nameKey', 'const'), cut('allc', 'block'), cut('allcSet', 'block'),
  cut('COHORT_ALIAS', 'const'), cut('cohortKey', 'const'),
  cut('rosterKey'), cut('latestPerStudent'),
  cut('mergeBaselineQ'),
  cut('unpackCohort'),
  cut('packCohort'),
  cut('bitsFor'), cut('bitW'), cut('bitR'), cut('b64url'), cut('unb64url'),
  /* 판 번호는 소스에서 그대로 읽는다. 여기에 손으로 적어 두면 링크 형식이
     바뀌어도 이 검사만 옛 판을 만들고 있게 된다 — 실제로 v3 로 올릴 때
     여기가 2 인 채로 남아 있었다. */
  cut('CS_VER', 'const'),
  'var CUR_YEAR=' + new Date().getFullYear() + ';',
  'function btoa(s){return Buffer.from(s,"binary").toString("base64");}',
  'function atob(s){return Buffer.from(s,"base64").toString("binary");}',
].join('\n'), ctx);

const examOf = id => EXAMS.find(e => e.id === id);
const acc = (exam, q) => (exam.multi && exam.multi[q]) ? exam.multi[q] : [exam.key[q - 1]];

/* 이 브라우저에서 채점한 학생들로 만든 cohortStats 의 알맹이 */
function localCS(exam, rows) {
  const N = rows.length, qp = [], qopt = [], qcnt = [];
  for (let q = 1; q <= exam.nQ; q++) {
    const opt = [0, 0, 0, 0]; let c = 0;
    rows.forEach(r => { const a = r[q - 1]; if (a >= 1 && a <= 4) opt[a - 1]++;
      if (acc(exam, q).indexOf(a) >= 0) c++; });
    qp.push(Math.round(c / N * 100)); qopt.push(opt.map(x => Math.round(x / N * 100))); qcnt.push(opt);
  }
  return { N, ready: true, estimated: false, percReady: true, qp, qopt, qcnt,
           totals: rows.map(r => r.filter((a, i) => acc(exam, i + 1).indexOf(a) >= 0).length),
           flagged: 0 };
}

console.log('── 저장된 집계가 앞뒤가 맞는다 ──');
/* ── 나중에 전원정답이 된 문항 ──────────────────────────────────────
   기준 기록은 그 회차를 채점하던 **당시의 규칙**으로 세어 둔 것이다. 뒤늦게
   전원정답으로 바꾼 문항은 정답자 수가 그때 그대로라 지금 규칙과 어긋난다.
   그건 데이터가 깨진 것이 아니라 시점이 다른 것이므로, 어느 문항인지 적어
   두고 넘어간다. 적어 두지 않은 새 어긋남은 그대로 빨간불이다.

   화면 정답률은 이 값을 쓰지 않는다 — 전원정답은 100% 로 덮는다
   (final.html mergeBaselineQ). 남는 것은 **점수 분포**뿐이다. 기준 기록의
   응시자들은 이 문항 점수를 못 받은 채로 들어 있어서, 그만큼 지금 채점하는
   학생이 석차에서 유리하다. 바로잡으려면 엑셀 원본에서 그 회차 기준 기록을
   다시 만들어야 한다(tools/gen_cohort_baseline.py) — 원본은 저장소에 없다. */
const LATER_ALLC = {
  'jmchc-9:50': '2026-07 전원정답 처리(선생님 지시) · 기준 기록 30명은 당시 규칙으로 채점됨',
};

{
  let holes = 0, cells = 0, bad = [];
  Object.keys(BASE).forEach(id => {
    const b = BASE[id], exam = examOf(id);
    if (!exam) { bad.push(id + ': exams.json 에 없다'); return; }
    /* ⚠ 여기서 그냥 b.qc.length 를 읽다가 **TypeError 로 죽은** 적이 있다.
       기준 기록 자동 갱신이 문항별 통계(q·qc)를 열 회차에서 통째로 지웠는데,
       검사는 "Cannot read properties of undefined" 만 뱉고 끝났다 —
       무엇이 없어졌는지 아무도 알 수 없다. 없으면 없다고 말한다. */
    if (!b.qc || !b.q) {
      /* 시트에서 만든 회차는 애초에 점수 분포만 갖는다 — 잃은 것이 아니다.
         그 자는 통계를 가진 회차를 덮지 않으므로(_baselineKeepWhy_),
         from:'sheet' 이면서 없는 것은 '처음부터 없던 것' 이다 (2026-08-19). */
      if (b.from !== 'sheet')
        bad.push(id + ': 문항별 통계(q·qc)가 없다 — 또래 정답률을 못 만든다');
      return;
    }
    if (b.qc.length !== exam.nQ) bad.push(id + ': qc 길이 ' + b.qc.length);
    if (b.q.length !== exam.nQ) bad.push(id + ': q 길이 ' + b.q.length);
    b.q.forEach((o, i) => { cells++;
      if (o === null) { holes++; return; }
      /* 엑셀이 '모두정답' 등으로 덮어쓴 칸은 빠지므로 합이 n 보다 작을 수 있다.
         하지만 넘을 수는 없다 — 넘으면 사람을 지어낸 것이다. */
      const sum = o.reduce((a, x) => a + x, 0);
      if (sum > b.n) bad.push(`${id} ${i + 1}번: 선택 분포 합 ${sum} > 응시 ${b.n}`);
      if (sum === 0) bad.push(`${id} ${i + 1}번: 아무도 없는데 null 이 아니다`);
      // 정답 보기를 고른 사람 수 = 정답자 수. 어긋나면 정답 키가 어긋난 것이다.
      // 칸이 덮이지 않은 문항에서만 견줄 수 있다(덮인 사람의 정답 여부는 채점 열에만 남았다)
      const mine = acc(exam, i + 1).reduce((a, k) => a + (o[k - 1] || 0), 0);
      if (sum === b.n && mine !== b.qc[i] && !LATER_ALLC[id + ':' + (i + 1)])
        bad.push(`${id} ${i + 1}번: 정답자 ${b.qc[i]} ≠ 선택 합 ${mine}`);
    });
    if (b.qc.some(c => c < 0 || c > b.n)) bad.push(id + ': 정답자 수가 응시 인원을 벗어난다');
    // 히스토그램 인원과 응시 인원이 같아야 한다(석차의 분모)
    const hn = Object.keys(b.hist).reduce((a, k) => a + b.hist[k], 0);
    if (hn !== b.n) bad.push(`${id}: hist 합 ${hn} ≠ n ${b.n}`);
  });
  chk('저장된 집계에 모순이 없다', bad.slice(0, 5), []);
  /* 적어 둔 예외가 실제로 어긋나 있는지도 본다. 어긋남이 사라졌는데 예외만
     남아 있으면(엑셀에서 다시 만든 뒤) 그 줄은 지워야 한다. */
  const stale = Object.keys(LATER_ALLC).filter(k => {
    const [id, qs] = k.split(':'), b = BASE[id], exam = examOf(id);
    if (!b || !exam) return true;
    const o = b.q[+qs - 1]; if (!o) return true;
    const sum = o.reduce((a, x) => a + x, 0);
    return !(sum === b.n && acc(exam, +qs).reduce((a, kk) => a + (o[kk - 1] || 0), 0) !== b.qc[+qs - 1]);
  });
  chk('쓸모없어진 예외가 남아 있지 않다', stale, []);
  /* 2026-08-10 에 화올·기출동형 열두 회차(827명)가 들어와 수가 크게 늘었다.
     16회차 387명 → 28회차 1214명. 여기 박아 둔 값은 **줄면 걸리라고** 있는
     것이지 늘지 말라는 것이 아니다 — 늘 때는 이 줄도 같이 올린다. */
  chk('문항 수', cells, 1680);
  /* 한 칸도 안 남은 문항. 전부 전원정답·모두정답 처리된 문항이라 분포를 따질
     것이 없다. 늘어나면 원본이 바뀌었거나 칸을 통째로 버리고 있다는 뜻이다. */
  chk('선택 분포가 없는 문항', holes, 11);
  // 일부만 덮인 문항은 남은 사람으로 센다. 통째로 버리면 이 수가 0이 된다.
  /* ⚠ 여기서 BASE[k].q 를 그냥 꺼내다 터졌다(2026-08-19). 시트에서 만드는 자는
     n·hist 만 만들기 때문에 **문항별 통계가 아예 없는 회차**가 생긴다. 없는 것은
     세지 않는다 — 있는 척 0 으로 세면 '일부만 남은 문항' 이 조용히 늘어난다. */
  const withQ = Object.keys(BASE).filter(k => BASE[k].q);
  chk('일부만 남은 문항', withQ.reduce((a, k) =>
    a + BASE[k].q.filter(o => o && o.reduce((x, y) => x + y, 0) !== BASE[k].n).length, 0), 8);
  /* 1214 → 1227 : 시트에서 KMChC 2025 제1차 심화(7명)·일반(6명)이 들어왔다.
     이 수는 **줄면 걸리라고** 있는 것이라 늘 때는 같이 올린다 (2026-08-19).
     1227 → 1235 : 기준 기록 자동 갱신 3회차(45bc2c1)로 8명이 들어왔다 (2026-08-21). */
  chk('기준 기록 인원', Object.keys(BASE).reduce((a, k) => a + BASE[k].n, 0), 1235);
}

console.log('\n── 나중에 전원정답이 된 문항의 또래 정답률 ──');
{
  /* 기준 기록의 정답자 수는 그때 규칙으로 센 것이라 실제보다 적다. 그 수를
     그대로 나누면 아무도 틀릴 수 없는 문항이 "또래 정답률 21%" 로 나온다.
     학부모가 받는 성적표에 그대로 찍히는 숫자다. */
  ctx.BASELINE = BASE;
  const exam = examOf('jmchc-9');
  const qcnt = Array.from({ length: exam.nQ }, () => [0, 0, 0, 0]);
  qcnt[49] = [1, 0, 0, 0];                       // 이번 학생은 ①을 골랐다(예전 규칙이면 오답)
  const cs = ctx.mergeBaselineQ(exam, { N: 1, percReady: true, qcnt, qp: [], qopt: [], totals: [30] });
  chk('50번은 100% 다', cs.qp[49], 100);
  chk('보통 문항은 기준 기록 그대로 센다', cs.qp[0] < 100, true);}

console.log('\n── 기준 기록이 정답률에 들어간다 ──');
{
  ctx.BASELINE = BASE;
  const exam = examOf('jmchc-6'), b = BASE['jmchc-6'];
  // 이 브라우저에서 채점한 학생 둘 — 1번에 ①, ④
  const rows = [
    Array.from({ length: 60 }, (_, i) => acc(exam, i + 1)[0]),          // 전부 정답
    Array.from({ length: 60 }, () => 1),                                 // 전부 ①
  ];
  const local = localCS(exam, rows);
  chk('합치기 전 또래는 2명', local.N, 2);
  const cs = ctx.mergeBaselineQ(exam, local);
  chk('합친 또래', cs.N, b.n + 2);
  chk('석차 모집단과 같은 수', cs.N, b.n + local.totals.length);

  // 1번: 기준 기록 [①1 ②0 ③0 ④10], 정답 ④. 우리 둘은 ④ 와 ①.
  chk('1번 선택 분포(사람 수)', cs.qcnt[0], [b.q[0][0] + 1, b.q[0][1], b.q[0][2], b.q[0][3] + 1]);
  const want = Math.round((b.qc[0] + 1) / cs.N * 100);
  chk('1번 정답률', cs.qp[0], want);
  chk('정답률이 2명짜리가 아니다', cs.qp[0] !== local.qp[0], true);

  // 저장된 정답자 수와 선택 분포에서 센 수가 어긋나면 안 된다(전 문항)
  let drift = 0;
  for (let q = 1; q <= exam.nQ; q++) {
    let c = 0; acc(exam, q).forEach(k => { c += cs.qcnt[q - 1][k - 1] || 0; });
    if (Math.round(c / cs.N * 100) !== cs.qp[q - 1]) drift++;
  }
  chk('정답률과 선택 분포가 같은 말을 한다', drift, 0);
}

console.log('\n── 답이 덮인 문항은 지어내지 않는다 ──');
{
  ctx.BASELINE = BASE;
  const exam = examOf('jmchc-9'), b = BASE['jmchc-9'];   // 47·60번이 '모두정답'
  const rows = [Array.from({ length: 60 }, () => 2), Array.from({ length: 60 }, () => 3)];
  const cs = ctx.mergeBaselineQ(exam, localCS(exam, rows));
  chk('47번은 선택 분포가 없다', b.q[46], null);
  chk('그 문항은 이번 응시자만 센다', cs.qcnt[46], [0, 1, 1, 0]);
  chk('분포가 100%를 넘지 않는다',
      cs.qopt[46].reduce((a, x) => a + x, 0) <= 100, true);
  // 정답자 수는 채점 열에 남아 있으므로 정답률에는 들어간다.
  chk('그래도 정답률은 합쳐 센다', cs.qp[46], Math.round((b.qc[46] + 2) / cs.N * 100));
  chk('모두정답이라 100%', cs.qp[46], 100);
  // 답이 온전한 문항은 정상적으로 합쳐진다.
  // qcnt 는 ①②③④ 만 센다 — 무응답은 여기 없고 정답률의 분모에만 들어간다.
  chk('1번은 합쳐진다', cs.qcnt[0].reduce((a, x) => a + x, 0), b.n - b.q[0][4] + 2);
}

console.log('\n── 일부만 덮인 문항은 남은 사람으로 센다 ──');
{
  ctx.BASELINE = BASE;
  const exam = examOf('jmchc-7'), b = BASE['jmchc-7'];   // 52번: 42명 중 1칸만 덮였다
  const q52 = b.q[51], kept = q52.reduce((a, x) => a + x, 0);
  chk('52번은 41명이 남아 있다', kept, b.n - 1);
  chk('통째로 버리지 않았다', q52 !== null, true);
  const rows = [Array.from({ length: 60 }, () => 2)];
  const cs = ctx.mergeBaselineQ(exam, localCS(exam, rows));
  // 분모는 b.n(42)이 아니라 남은 41 + 이번 1명 = 42
  const den = kept + 1;
  chk('네 보기 모두 남은 사람 수로 나눈다', cs.qopt[51],
      [0, 1, 2, 3].map(k => Math.round((q52[k] + (k === 1 ? 1 : 0)) / den * 100)));
  chk('선택 비율의 합이 100을 넘지 않는다',
      cs.qopt[51].reduce((a, x) => a + x, 0) <= 100, true);

  /* 분모를 어디서 가져오는지가 핵심이다. 덮인 칸까지 분모에 넣으면(b.n) 비율이
     실제보다 낮게 나온다. 덮인 칸이 많은 59번(42명 중 26칸이 덮여 16명만 남음)
     에서는 그 차이가 눈에 띄게 벌어진다. */
  const q59 = b.q[58], kept59 = q59.reduce((a, x) => a + x, 0);
  chk('59번은 16명만 남아 있다', kept59, 16);
  const den59 = kept59 + 1;
  chk('59번도 남은 사람 수로 나눈다', cs.qopt[58],
      [0, 1, 2, 3].map(k => Math.round((q59[k] + (k === 1 ? 1 : 0)) / den59 * 100)));
  chk('덮인 칸을 분모에 넣은 값과 다르다',
      cs.qopt[58][3] !== Math.round(q59[3] / (b.n + 1) * 100), true);
}

console.log('\n── 공유 링크는 길어지지 않는다 ──');
{
  ctx.BASELINE = BASE;
  const exam = examOf('jmchc-6');
  const rows = Array.from({ length: 3 }, (_, i) =>
    Array.from({ length: 60 }, (_, q) => ((i + q) % 4) + 1));
  const cs = ctx.mergeBaselineQ(exam, localCS(exam, rows));
  const packed = ctx.packCohort(exam, cs);
  chk('링크가 만들어진다', packed.length > 0, true);
  // 합쳐진 14명을 실으면 칸마다 비트가 늘어 주소가 길어진다. 3명만 싣는다.
  const naive = ctx.packCohort(exam, Object.assign({}, cs, { local: null }));
  chk('합친 인원을 싣지 않는다', packed.length < naive.length, true);

  // 받는 쪽: 링크만 풀면 3명, 자기 baseline.json 을 얹으면 보낸 쪽과 같아진다.
  const raw = ctx.unpackCohort(exam, packed);
  chk('링크에 담긴 또래', raw.N, 3);
  const rebuilt = ctx.mergeBaselineQ(exam, raw);
  chk('받는 쪽 또래 수가 같다', rebuilt.N, cs.N);
  chk('받는 쪽 정답률이 같다', rebuilt.qp, cs.qp);
  chk('받는 쪽 선택 분포가 같다', rebuilt.qopt, cs.qopt);
}

console.log('\n── 한 학생은 한 명으로 센다 ──');
{
  /* 같은 학생을 두 번 채점하면(오타를 고치고 다시 채점하는 일이 흔하다) 답안이
     조금이라도 다르면 기록이 두 줄 남는다. 통계가 둘을 각각 세면 또래 인원이
     부풀어, 시트(학생별 최신 1건)와 어긋난다 — 화면 14명 · 문자 13명. */
  const r = (name, school, ts, ans) => ({ name, school, grade: '2', ts, ans, correct: 0 });
  const got = ctx.latestPerStudent([
    r('김철수', 'A중', 1, [1, 1]), r('김철수', 'A중', 2, [2, 2]),   // 같은 학생, 다시 채점
    r('김철수', 'B중', 1, [3, 3]),                                   // 동명이인 — 다른 사람
    r('이영희', 'A중', 1, [4, 4]),
  ]);
  chk('네 줄이 세 사람이 된다', got.length, 3);
  chk('같은 학생은 최신 것만 남는다',
      got.filter(x => x.name === '김철수' && x.school === 'A중').map(x => x.ans), [[2, 2]]);
  chk('동명이인은 살아남는다',
      got.filter(x => x.name === '김철수').length, 2);
  chk('순서가 뒤집히지 않는다', got.map(x => x.name), ['김철수', '김철수', '이영희']);
  // 저장 시각이 없어도 죽지 않는다(옛 기록)
  chk('ts 가 없어도 한 명으로 센다',
      ctx.latestPerStudent([r('박', 'C중', undefined, [1]), r('박', 'C중', undefined, [2])]).length, 1);

  // 성적표가 실제로 이 함수를 통하는지 — 안 통하면 화면만 예전 그대로다
  chk('cohortStats 가 학생별로 묶는다',
      /latestPerStudent\(subs\(exam\.id\)/.test(SRC), true);
}

console.log('\n── 성적표가 실제로 이 함수를 통한다 ──');
{
  // 위 검사는 mergeBaselineQ 만 직접 부른다. 정작 cohortStats 가 그걸
  // 안 부르면 화면은 예전 숫자 그대로인데 테스트만 초록불이 된다.
  const body = SRC.slice(SRC.indexOf('function cohortStats('),
                         SRC.indexOf('function percentile('));
  chk('cohortStats 가 합쳐서 돌려준다',
      /return mergeBaselineQ\(exam,\{N,ready:true/.test(body), true);
  chk('공유 링크로 열었을 때도 합친다',
      /return mergeBaselineQ\(exam,window\.__csLink\.parsed\)/.test(body), true);
  // 링크에 실을 때는 이 브라우저 사람만 — cs.N(합친 수)을 쓰면 주소가 길어진다.
  const pack = SRC.slice(SRC.indexOf('function packCohort('),
                         SRC.indexOf('function unpackCohort('));
  chk('링크는 local 을 싣는다', /var L=cs\.local\|\|/.test(pack), true);
  chk('링크가 합친 인원을 안 쓴다', /Math\.min\(65535,L\.N/.test(pack), true);
}

console.log('\n── 기준 기록이 없으면 예전 그대로 ──');
{
  ctx.BASELINE = BASE;
  /* 기준 기록이 **없는** 회차를 골라야 이 검사가 뜻을 가진다. 예전에는
     'sanyeom-60' 이라고 손으로 적어 두었는데, 그 회차 엑셀이 들어오자
     검사가 통째로 뒤집혔다. 이름을 적지 말고 없는 것을 찾아 쓴다. */
  const exam = EXAMS.filter(e => !BASE[e.id])[0];
  chk('기준 기록이 없는 회차가 하나는 있다', !!exam, true);
  const rows = [Array.from({ length: exam.nQ }, () => 1),
                Array.from({ length: exam.nQ }, () => 2)];
  const local = localCS(exam, rows);
  const cs = ctx.mergeBaselineQ(exam, local);
  chk('또래 수가 그대로', cs.N, 2);
  chk('정답률이 그대로', cs.qp, local.qp);
}
{
  // baseline.json 이 아직 안 왔을 때도 죽지 않는다
  ctx.BASELINE = null;
  const exam = examOf('jmchc-6');
  const local = localCS(exam, [Array.from({ length: 60 }, () => 1)]);
  chk('기준 기록 없이도 통과', ctx.mergeBaselineQ(exam, local).N, 1);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
