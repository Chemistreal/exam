/* ============================================================
   석차 모집단 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   석차·백분위는 그때까지 **이 브라우저에 채점해 둔 학생 수**를 모집단으로
   삼았다. 그래서 같은 시험인데 학생마다 숫자가 달랐다.

       김규민  3/9      ← 9명 채점했을 때 본 화면
       김시헌  8/10     ← 한 명 더 채점한 뒤
       이도현  (없음)   ← 8명이 되기 전에 본 화면

   같은 회차를 같이 본 학생들인데 모집단이 셋 다 다르다. 이러면 석차는
   뜻이 없다. 한 회차를 실제로 응시한 사람은 성적표 엑셀에 다 들어 있으므로
   그 점수 분포(cohort/baseline.json)를 모집단으로 쓴다.

   엑셀 명단과 지금 채점하는 학생은 서로 다른 사람들이므로 **더한다.**
   대신해 버리면 새로 채점한 학생이 모집단에서 통째로 빠진다.

   여기서 지키는 것:
   - 분모 = 기준표 인원 + 그때까지 채점한 인원
   - 한 명만 채점해도 석차가 나온다(예전에는 8명 전이면 통째로 빈칸)
   - 화면 두 곳(요약·점수 분포)이 같은 숫자를 말한다
   - 기준표에 이름·학교가 새어 들어가지 않는다
   - 기준표가 없는 회차는 예전대로 이 브라우저 기록으로 센다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/rank-baseline.js
   ============================================================ */
'use strict';
/* 검사가 운영 시트를 읽으면 실 데이터가 심어 둔 데이터를 덮는다.
   실제로 CI 에서 그렇게 깨졌다 — tests/_nosheet.js 의 주석 참고. */
const noSheet = require('./_nosheet.js');
const fs = require('fs');
const path = require('path');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const U = `http://localhost:${PORT}/final.html`;

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  /* 브라우저를 깔아 놓고도 조용히 건너뛰면 초록불이 '브라우저 검사까지
     통과했다' 로 읽힌다. 실제로 그랬다 — 통합 셸의 브라우저 검사가 몇 달
     동안 CI 에서 한 번도 안 돌았는데 초록불이었다. 깔아 둔 자리에서는 멈춘다. */
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* 화면에 뜬 **연도누적 총석차**만 긁는다. 2026년 반석차는 모집단이 다르다
   (기준 기록을 안 쓰고 올해 채점한 학생만) — 그것까지 섞어 세면 이 파일이
   보려는 '기준 기록이 분모에 들어갔나' 가 흐려진다.

   innerText 로 한 번에 긁으면 안 된다: 맨 위 상자는 숫자가 이름보다 **앞**에
   오므로 '연도누적 총석차' 뒤에서 반석차 숫자를 집어 온다. 상자는 DOM 으로,
   '점수 분포 속 나의 위치' 는 그 섹션 안에서만 찾는다. */
const RANKS = `(function(){ var out=[];
  [].forEach.call(document.querySelectorAll('.fhds'),function(d){
    var v=((d.querySelector('b')||{}).textContent||'').trim();
    var L=((d.querySelector('span')||{}).textContent||'');
    if(/연도누적 총석차/.test(L)) out.push(v);
  });
  var sec=[].filter.call(document.querySelectorAll('.sec'),function(x){
    return /점수 분포 속 나의 위치/.test(x.textContent); })[0];
  if(sec){ var m=(sec.innerText||'').replace(/\\s+/g,' ').match(/연도누적 총석차 (\\d+\\/\\d+)/);
    if(m) out.push(m[1]); }
  return out; })()`;

(async () => {
  // ── 1부. 파일 자체 ──────────────────────────────────────────────
  console.log('── 기준표 파일 ──');
  const raw = fs.readFileSync(path.join(__dirname, '..', 'cohort', 'baseline.json'), 'utf8');
  const base = JSON.parse(raw);
  const ids = Object.keys(base.exams || {});
  chk('회차가 담겨 있다', ids.length > 0, true);
  // 값이 전부 숫자여야 한다. 이름이 섞이면 여기서 걸린다.
  const shapeOK = ids.every(id => {
    const e = base.exams[id];
    return typeof e.n === 'number' && e.hist &&
      Object.entries(e.hist).every(([k, v]) => /^\d+$/.test(k) && Number.isInteger(v) && v > 0);
  });
  chk('히스토그램이 숫자뿐이다', shapeOK, true);
  // 사람 이름이 들어갈 자리가 없어야 한다 — exams 안에 한글이 하나도 없다
  const body = raw.slice(raw.indexOf('"exams"'));
  chk('exams 안에 한글이 없다(이름 유출 방지)', (body.match(/[가-힣]/g) || []).length, 0);
  const sums = ids.every(id => base.exams[id].n ===
    Object.values(base.exams[id].hist).reduce((a, b) => a + b, 0));
  chk('n 과 히스토그램 합이 맞는다', sums, true);
  const total = ids.reduce((a, id) => a + base.exams[id].n, 0);
  console.log(`  ${ids.length}개 회차 · ${total}명`);

  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });
  /* ⚠ 브라우저에 건다 — 화면 하나에 걸면 나중에 여는 화면이 샌다. */
  await noSheet(browser);
  const errs = [];

  // ── 2부. 기준표 + 이 브라우저 기록 ──────────────────────────────
  console.log('\n── 기준표 + 채점 기록 ──');
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push(e.message));
  await page.goto(U, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);

  const loaded = await page.evaluate(() => ({ ok: !!BASELINE, n: BASELINE && BASELINE['jmchc-6'] && BASELINE['jmchc-6'].n }));
  chk('앱이 기준표를 읽었다', loaded.ok, true);
  chk('jmchc-6 모집단 인원', loaded.n, base.exams['jmchc-6'].n);

  // 학생을 한 명씩 채점하며, 매번 분모가 기준표 + 채점 인원인지 본다
  const seen = await page.evaluate(async (RANKS_SRC) => {
    localStorage.clear();
    const out = [];
    const students = [['이도현', 3], ['김규민', 5], ['김시헌', 7]];
    for (const [nm, step] of students) {
      openExam('jmchc-6');
      document.getElementById('nm').value = nm;
      for (let q = 1; q <= cur.nQ; q++) setAns(q, (q % step === 0) ? ((cur.key[q - 1] % 4) + 1) : cur.key[q - 1]);
      scoreAuto();
      await new Promise(r => setTimeout(r, 2200));
      out.push({ nm, ranks: eval(RANKS_SRC), locals: subs('jmchc-6').length });
    }
    return out;
  }, RANKS);
  seen.forEach(s => console.log(`  ${s.nm}  ${s.ranks.join(' · ')}   (이 브라우저 기록 ${s.locals}명)`));

  chk('세 학생 모두 석차가 나온다', seen.every(s => s.ranks.length >= 2), true);
  chk('한 명만 채점해도 나온다(예전엔 8명 전이면 빈칸)', seen[0].ranks.length >= 2, true);
  /* 기준표와 이 브라우저 기록을 **더한다.** 엑셀에 든 사람과 지금 채점하는
     사람이 전혀 다른 학생들이라고 하셨다. 겹치지 않으면 더하는 것이 맞다 —
     대신하면 새로 채점한 학생이 모집단에서 통째로 빠진다.
     그래서 분모는 채점하는 동안 기준표 인원 + 그때까지 채점한 인원이다. */
  seen.forEach(s => {
    const denom = Number(s.ranks[0].split('/')[1]);
    chk(`분모 = 기준표 ${loaded.n} + 채점 ${s.locals} · ${s.nm}`, denom, loaded.n + s.locals);
  });
  chk('기준표만 쓰지 않는다(새 학생이 빠지면 안 된다)',
      Number(seen[seen.length - 1].ranks[0].split('/')[1]) > loaded.n, true);
  seen.forEach(s => chk(`화면 두 곳이 일치 · ${s.nm}`, Array.from(new Set(s.ranks)), s.ranks.slice(0, 1)));
  // 점수가 다르면 등수도 달라야 한다(전부 같은 등수로 나오면 뭔가 잘못된 것)
  chk('학생마다 등수가 다르다', new Set(seen.map(s => s.ranks[0])).size > 1, true);

  // ── 3부. 기준표가 없는 회차는 예전 방식 ─────────────────────────
  console.log('\n── 기준표가 없는 회차 ──');
  const noBase = await page.evaluate(async (RANKS_SRC) => {
    localStorage.clear();
    const ex = FINAL_EXAMS.find(e => !BASELINE[e.id]);
    if (!ex) return null;
    openExam(ex.id);
    document.getElementById('nm').value = '홍길동';
    for (let q = 1; q <= cur.nQ; q++) setAns(q, cur.key[q - 1]);
    scoreAuto();
    await new Promise(r => setTimeout(r, 2200));
    return { id: ex.id, ranks: eval(RANKS_SRC) };
  }, RANKS);
  if (noBase) {
    console.log(`  ${noBase.id} → ${noBase.ranks.join(' · ') || '(이 브라우저 기록만)'}`);
    // 이 브라우저 기록 1명뿐이니 1/1 이 나온다 — 기준표를 잘못 갖다 붙이지 않았다는 뜻
    chk('기준표 인원을 빌려 쓰지 않는다', noBase.ranks.every(r => r.endsWith('/1')), true);
  }

  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
