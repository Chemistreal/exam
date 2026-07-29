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
  const head = kind === 'const' ? new RegExp(`^const ${name}=`, 'm')
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
  cut('accSet', 'const'),
  cut('mergeBaselineQ'),
  cut('unpackCohort'),
  cut('packCohort'),
  cut('bitsFor'), cut('bitW'), cut('bitR'), cut('b64url'), cut('unb64url'),
  'const CS_VER=2;',
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
{
  let holes = 0, cells = 0, bad = [];
  Object.keys(BASE).forEach(id => {
    const b = BASE[id], exam = examOf(id);
    if (!exam) { bad.push(id + ': exams.json 에 없다'); return; }
    if (b.qc.length !== exam.nQ) bad.push(id + ': qc 길이 ' + b.qc.length);
    if (b.q.length !== exam.nQ) bad.push(id + ': q 길이 ' + b.q.length);
    b.q.forEach((o, i) => { cells++;
      if (o === null) { holes++; return; }
      if (o.reduce((a, x) => a + x, 0) !== b.n) bad.push(`${id} ${i + 1}번: 선택 분포 합 ≠ ${b.n}`);
      // 정답 보기를 고른 사람 수 = 정답자 수. 어긋나면 정답 키가 어긋난 것이다.
      const mine = acc(exam, i + 1).reduce((a, k) => a + (o[k - 1] || 0), 0);
      if (mine !== b.qc[i]) bad.push(`${id} ${i + 1}번: 정답자 ${b.qc[i]} ≠ 선택 합 ${mine}`);
    });
    if (b.qc.some(c => c < 0 || c > b.n)) bad.push(id + ': 정답자 수가 응시 인원을 벗어난다');
    // 히스토그램 인원과 응시 인원이 같아야 한다(석차의 분모)
    const hn = Object.keys(b.hist).reduce((a, k) => a + b.hist[k], 0);
    if (hn !== b.n) bad.push(`${id}: hist 합 ${hn} ≠ n ${b.n}`);
  });
  chk('저장된 집계에 모순이 없다', bad.slice(0, 5), []);
  chk('문항 수', cells, 900);
  // 엑셀이 '모두정답' 등으로 학생 답을 덮어쓴 문항. 늘어나면 원본이 바뀐 것이다.
  chk('선택 분포가 없는 문항', holes, 8);
  chk('기준 기록 인원', Object.keys(BASE).reduce((a, k) => a + BASE[k].n, 0), 365);
}

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
  // 정답자 수는 채점 열에 남아 있으므로 정답률에는 들어간다.
  chk('그래도 정답률은 합쳐 센다', cs.qp[46], Math.round((b.qc[46] + 2) / cs.N * 100));
  chk('모두정답이라 100%', cs.qp[46], 100);
  // 답이 온전한 문항은 정상적으로 합쳐진다.
  // qcnt 는 ①②③④ 만 센다 — 무응답은 여기 없고 정답률의 분모에만 들어간다.
  chk('1번은 합쳐진다', cs.qcnt[0].reduce((a, x) => a + x, 0), b.n - b.q[0][4] + 2);
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
  const exam = examOf('sanyeom-60') || examOf('donghyung-1');
  chk('이 시험엔 기준 기록이 없다', !BASE[exam.id], true);
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
