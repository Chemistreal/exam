/* ============================================================
   공유 링크 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   `#r=` 링크는 답안만 담고, 받는 쪽 브라우저에서 처음부터 다시 채점한다.
   그래서 두 가지 문제가 있었다.

   1) 또래 통계가 빈칸이었다. 학부모 브라우저에는 누적 응시 기록이 없으니
      cohortStats 가 계산할 것이 없다. 정작 "우리 아이가 또래 대비 어디쯤인가"가
      학부모가 가장 보고 싶어 하는 것이다.
      → 링크에 **합계만** 실어 보낸다(문항별 정답률·선택 분포·점수 분포).
        이름도 답안지도 보내지 않으므로 개인은 드러나지 않는다.

   2) 이름이 평문이었다. `#r=...홍길동` 은 단톡방 미리보기에 뜨고 주소창과
      방문 기록에도 남는다.
      → base64 로 감싼다. 암호가 아니라, 눈에 띄어 새는 것을 막는 것이다.
        `~` 로 시작하면 새 방식, 아니면 예전 링크라 그대로 읽는다.

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/share-link.js
   ============================================================ */
'use strict';
/* 멈추는 검사는 실패하는 검사보다 나쁘다 — tests/_watchdog.js 주석 참고. */
require('./_watchdog.js')(240);
/* 검사가 진짜 시트에 쓰면 안 된다. 실제로 CI 가 돌 때마다 파이널 앱이
   진짜 앱스크립트로 제출해서, 홍길동·예비본 같은 줄이 학생들 석차
   모집단에 섞여 들어갔다. 브라우저를 띄우자마자 그 길을 끊는다. */
const seal = require('./_seal.js');
/* 검사가 운영 시트를 읽으면 실 데이터가 심어 둔 데이터를 덮는다.
   실제로 CI 에서 그렇게 깨졌다 — tests/_nosheet.js 의 주석 참고. */
const noSheet = require('./_nosheet.js');
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
  console.log('건너뜀: playwright 를 찾지 못했다 (PLAYWRIGHT_MODULE 로 경로 지정)'); process.exit(0);
}

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* ── 1부. 또래 통계 스냅숏 ───────────────────────────────────────── */
async function cohortSnapshot(browser, errs) {
  console.log('── 또래 통계 스냅숏 ──');

  // 선생님 브라우저: 12명 누적(MINP=8 을 넘겨야 통계가 켜진다) → 공유 링크
  const teacher = await browser.newPage();
  teacher.on('pageerror', e => errs.push('교사: ' + e.message));
  await teacher.goto(U, { waitUntil: 'networkidle' });
  const made = await teacher.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2018'), nQ = ex.nQ;
    // 학생마다 서로 다른 답안지(같으면 cleanCohort 가 '패턴 복제'로 걸러낸다)
    const mk = s => { let x = (s * 2654435761) >>> 0, a = [];
      for (let i = 0; i < nQ; i++) { x = (x * 1664525 + 1013904223) >>> 0; a.push((x >>> 16) % 4 + 1); }
      return a; };
    const miss = new Set(ex.miss || []), arr = [];
    for (let s = 1; s <= 12; s++) {
      const ans = mk(s); let c = 0, tot = 0;
      for (let q = 1; q <= nQ; q++) { if (miss.has(q)) continue; tot++; if (okq(ex, q, ans[q - 1])) c++; }
      arr.push({ name: '학생' + s, school: 'X중', grade: '3', ts: 1000 + s,
                 correct: c, total: tot, wrong: tot - c, ans: ans });
    }
    saveSubs('hwol-2018', arr);
    const cs = cohortStats(ex);
    const sel2 = {}; mk(3).forEach((v, i) => { sel2[i + 1] = v; });
    const link = shareLinkFinal(ex, sel2, '홍길동', '');
    return { N: cs.N, ready: cs.percReady, qp0: cs.qp && cs.qp[0], qopt0: cs.qopt && cs.qopt[0],
             totals: cs.totals.slice().sort((a, b) => a - b),
             qp: cs.qp, qopt: cs.qopt, nQ,
             link, snapLen: (link.match(/#s=([^&]+)&/) || [, ''])[1].length,
             short: (() => { try { localStorage.setItem('chemistreal:final:cslink', '0'); } catch (e) {}
                             const s = shareLinkFinal(ex, sel2, '홍길동', '');
                             try { localStorage.setItem('chemistreal:final:cslink', '1'); } catch (e) {}
                             return s; })() };
  });
  console.log(`  교사 쪽: N=${made.N} 1번 정답률=${made.qp0} · 링크 ${made.link.length}자 (스냅숏 ${made.snapLen}자)`);
  chk('교사 쪽 또래 통계 활성', made.ready, true);
  /* ⚠ `#s=…&r=` 로 **붙여서** 보면 안 된다. `r=` 앞에는 이름=값 칸이 몇 개든
     온다(채점일 `t=` 가 2026-08-11 에 늘었다). 그날 이 자를 포함해 셋이
     한꺼번에 빨간불이 났다 — 규칙은 final.html 의 shareLinkFinal 위에 적어
     두었다. **자가 코드보다 좁으면, 코드가 자란 날 자가 먼저 운다.** */
  chk('링크에 s= 스냅숏이 들어감',
      /#([a-z]+=[^&]*&)*s=[A-Za-z0-9_-]+&/.test(made.link) && /[#&]r=/.test(made.link),
      true);
  /* 처음 형식은 문항당 6바이트(정답률·①②③④·변별도)를 그대로 담아 60문항이면
     567자였다. 카톡으로 보내기에 너무 길다는 말을 들었다. 변별도는 아무 데서도
     안 읽었고, 정답률은 선택 분포에서 다시 나오고, 비율 대신 사람 수를 남은
     폭만큼만 담으면 된다. 이 한계가 그 세 가지를 함께 지킨다. */
  chk('스냅숏이 문항당 3자 아래로 줄었다', made.snapLen < made.nQ * 3, true);
  // 통째로 끄면 답안만 담은 짧은 주소가 나온다
  chk('스위치를 끄면 s= 가 빠진다', /#s=/.test(made.short), false);
  chk('끈 링크가 켠 링크보다 짧다', made.short.length < made.link.length - 100, true);
  await teacher.close();

  // 학부모 브라우저: 누적 기록이 하나도 없다
  const parent = await browser.newPage();
  parent.on('pageerror', e => errs.push('학부모: ' + e.message));
  await parent.goto(made.link, { waitUntil: 'networkidle' });
  await parent.waitForTimeout(2500);
  const seen = await parent.evaluate(() => {
    const cs = cohortStats(FINAL_EXAMS.find(e => e.id === 'hwol-2018'));
    return { N: cs.N, ready: cs.percReady, fromLink: !!cs.fromLink,
             qp0: cs.qp && cs.qp[0], qopt0: cs.qopt && cs.qopt[0],
             qp: cs.qp, qopt: cs.qopt,
             totals: cs.totals.slice().sort((a, b) => a - b),
             peerText: document.body.innerText.includes('또래') };
  });
  chk('학부모 쪽에도 또래 통계가 뜬다', seen.ready, true);
  chk('링크에서 온 것으로 표시', seen.fromLink, true);
  chk('인원수 그대로', seen.N, made.N);
  chk('1번 정답률 그대로', seen.qp0, made.qp0);
  chk('1번 선택 분포 그대로', seen.qopt0, made.qopt0);
  // 한 문항만 맞으면 놓치는 것이 있다. 줄이면서 정답률은 아예 담지 않고
  // 선택 분포에서 다시 계산하므로, 전 문항이 맞아떨어져야 한다.
  chk('전 문항 정답률 그대로', seen.qp, made.qp);
  chk('전 문항 선택 분포 그대로', seen.qopt, made.qopt);
  chk('점수 분포 그대로(백분위 계산용)', seen.totals, made.totals);
  chk('화면에 또래 문구가 나온다', seen.peerText, true);
  await parent.close();
}

/* ── 1.5부. 옛 형식(v1) 링크 ─────────────────────────────────────────
   문항당 6바이트짜리 링크가 이미 학부모에게 나갔다. 형식을 줄였다고
   그 링크들이 빈 성적표가 되면 안 된다. 손으로 v1 바이트를 만들어 읽힌다. */
async function legacySnapshot(browser, errs) {
  console.log('\n── 옛 형식(v1) 링크 ──');
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push('v1: ' + e.message));
  await page.goto(U, { waitUntil: 'networkidle' });
  const got = await page.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2018'), nQ = ex.nQ, N = 12;
    const miss = new Set(ex.miss || []);
    const out = [1, nQ, N >> 8, N & 255], want = { qp: [], qopt: [] };
    for (let q = 1; q <= nQ; q++) {
      if (miss.has(q)) { out.push(255, 0, 0, 0, 0, 255); want.qp.push(null); want.qopt.push(null); continue; }
      const p = (q * 7) % 101, o = [(q * 3) % 40, (q * 11) % 30, (q * 5) % 20, (q * 13) % 25];
      out.push(p, o[0], o[1], o[2], o[3], 120);
      want.qp.push(p); want.qopt.push(o);
    }
    for (let t = 0; t <= nQ; t++) out.push(t === 30 ? 7 : (t === 40 ? 5 : 0));
    const cs = unpackCohort(ex, b64url(Uint8Array.from(out)));
    return { ok: !!cs, N: cs && cs.N, qp: cs && cs.qp, qopt: cs && cs.qopt,
             totals: cs && cs.totals.length, want };
  });
  chk('v1 링크가 그대로 읽힌다', got.ok, true);
  chk('v1 인원수', got.N, 12);
  chk('v1 정답률 전 문항', got.qp, got.want.qp);
  chk('v1 선택 분포 전 문항', got.qopt, got.want.qopt);
  chk('v1 점수 분포', got.totals, 12);
  await page.close();
}

/* ── 1.7부. 반석차도 링크에 실린다 ────────────────────────────────────
   선생님 화면에는 「2026년 반석차 3/5」가 나오는데, 보내 준 링크를 학부모가
   열면 그 줄만 통째로 없었다. 링크에 점수 분포는 실었지만 **몇 해에 낸
   점수인지**를 안 실어서, 받는 쪽에서는 올해 것을 골라낼 수가 없었다.
   같은 성적표를 두고 서로 다른 숫자를 이야기하게 된다.

   그래서 v3 는 올해 점수 분포와 연도를 함께 싣는다. 이미 나간 v2 링크는
   반석차만 빠진 채 나머지가 그대로 읽혀야 한다. */
async function yearRankSnapshot(browser, errs) {
  console.log('\n── 반석차가 링크를 타고 간다 ──');
  const YEAR = new Date().getFullYear();

  const teacher = await browser.newPage();
  teacher.on('pageerror', e => errs.push('교사(반석차): ' + e.message));
  await teacher.goto(U, { waitUntil: 'networkidle' });
  const made = await teacher.evaluate(yr => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2018'), nQ = ex.nQ;
    const mk = s => { let x = (s * 2654435761) >>> 0, a = [];
      for (let i = 0; i < nQ; i++) { x = (x * 1664525 + 1013904223) >>> 0; a.push((x >>> 16) % 4 + 1); }
      return a; };
    const miss = new Set(ex.miss || []), arr = [];
    // 12명 중 앞 7명만 올해 채점했다. 나머지는 작년 학생 — 반석차에서 빠져야 한다.
    for (let s = 1; s <= 12; s++) {
      const ans = mk(s); let c = 0, tot = 0;
      for (let q = 1; q <= nQ; q++) { if (miss.has(q)) continue; tot++; if (okq(ex, q, ans[q - 1])) c++; }
      arr.push({ name: '학생' + s, school: 'X중', grade: '3',
                 ts: Date.UTC(s <= 7 ? yr : yr - 1, 5, 1) + s * 1000,
                 correct: c, total: tot, wrong: tot - c, ans: ans });
    }
    saveSubs('hwol-2018', arr);
    const cs = cohortStats(ex), ry = rankPoolYear(ex, cs);
    const sel2 = {}; mk(3).forEach((v, i) => { sel2[i + 1] = v; });
    const link = shareLinkFinal(ex, sel2, '홍길동', '');
    // 이미 나간 v2 링크: 앞부분 형식이 v3 와 같아서 판 번호만 되돌리면 그대로다
    const raw = unb64url((link.match(/#s=([^&]+)&/) || [, ''])[1]);
    raw[0] = 2;
    const v2 = unpackCohort(ex, b64url(raw));
    /* 기준 기록(cohort/baseline.json)이 있는 회차는 통계가 mergeBaselineQ 를
       한 번 더 지난다. 거기서 연도를 흘리면 링크로 잘 받아 놓고도 반석차가
       사라진다 — 실제로 그 자리가 통계를 통째로 새로 만든다. */
    const bex = FINAL_EXAMS.find(e => BASELINE && BASELINE[cohortKey(e.id)] && BASELINE[cohortKey(e.id)].qc);
    const kept = bex ? mergeBaselineQ(bex, { N: 3, ready: true, estimated: false, percReady: true,
        qp: [], qopt: [], qcnt: new Array(bex.nQ).fill([0, 0, 0, 0]),
        totals: [10, 20, 30], yearTotals: [10, 20], yearOf: 2025, fromLink: true }) : null;
    return { N: cs.N, localN: cs.totals.length, totals: cs.totals.slice().sort((a, b) => a - b),
             baseEx: bex && bex.id, keptYear: kept && kept.yearOf,
             keptYearTotals: kept && (kept.yearTotals || []).length,
             yearTotals: (cs.yearTotals || []).slice().sort((a, b) => a - b),
             yready: ry.ready, yN: ry.N, yyear: ry.year, link,
             v2ok: !!v2, v2N: v2 && v2.N,
             v2totals: v2 && v2.totals.slice().sort((a, b) => a - b),
             v2year: v2 && (v2.yearTotals || []).length };
  }, YEAR);
  console.log(`  교사 쪽: 누적 ${made.N}명 · 올해 ${made.yN}명 (${made.yyear}년)`);
  chk('교사 쪽 올해 인원', made.yN, 7);
  chk('교사 쪽 반석차가 켜진다', made.yready, true);
  chk('작년 학생은 올해에서 빠진다', made.yearTotals.length < made.totals.length, true);
  chk('기준 기록을 얹어도 연도가 남는다', made.keptYear, 2025);
  chk('기준 기록을 얹어도 올해 분포가 남는다', made.keptYearTotals, 2);

  const parent = await browser.newPage();
  parent.on('pageerror', e => errs.push('학부모(반석차): ' + e.message));
  await parent.goto(made.link, { waitUntil: 'networkidle' });
  await parent.waitForTimeout(2500);
  const seen = await parent.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'hwol-2018');
    const cs = cohortStats(ex), ry = rankPoolYear(ex, cs);
    return { mine: (subs('hwol-2018') || []).length,
             totals: cs.totals.slice().sort((a, b) => a - b),
             yearTotals: (cs.yearTotals || []).slice().sort((a, b) => a - b),
             yearOf: cs.yearOf, yready: ry.ready, yN: ry.N, yyear: ry.year,
             text: document.body.innerText };
  });
  /* 학부모 브라우저에 남는 기록은 방금 다시 채점한 이 학생 하나뿐이다.
     나머지 숫자는 전부 링크에서 온 것이라야 한다. */
  chk('학부모 브라우저 기록은 이 학생 하나뿐', seen.mine, 1);
  chk('그런데도 올해 인원이 여럿', seen.yearTotals.length > 1, true);
  chk('올해 점수 분포가 링크를 타고 왔다', seen.yearTotals, made.yearTotals);
  chk('누적 점수 분포는 그대로', seen.totals, made.totals);
  chk('링크에 적힌 연도를 읽었다', seen.yearOf, YEAR);
  chk('학부모 쪽에서도 반석차가 켜진다', seen.yready, true);
  chk('올해 인원 그대로', seen.yN, made.yN);
  chk('연도 라벨이 교사 화면과 같다', seen.yyear, made.yyear);
  // 여기가 이 검사의 이유다. 숫자가 맞아도 화면에 안 나오면 없는 것과 같다.
  chk('성적표에 반석차 줄이 보인다', seen.text.includes(YEAR + '년 반석차'), true);
  chk('총석차도 그대로 보인다', seen.text.includes('연도누적 총석차'), true);
  await parent.close();
  await teacher.close();

  // 이미 나간 v2 링크 — 반석차만 빠지고 나머지는 살아 있어야 한다
  chk('v2 링크가 계속 읽힌다', made.v2ok, true);
  /* 링크가 싣는 인원은 **이 브라우저에 채점해 둔 사람**뿐이다. 기준 기록은
     링크에 안 싣고 받는 쪽이 baseline.json 으로 얹는다(주소를 늘릴 이유가
     없다). 그래서 cs.N 은 기준 기록까지 더한 수라 링크 쪽 수와 다르다 —
     hwol-2018 에 103명이 들어오자 12 vs 115 가 되어 걸렸다. 링크가 싣기로 한
     것과 견준다. */
  chk('v2 인원수 그대로', made.v2N, made.localN);
  chk('v2 점수 분포 그대로', made.v2totals, made.totals);
  chk('v2 에는 올해 분포가 없다', made.v2year, 0);
}

/* ── 2부. 이름 감싸기 ────────────────────────────────────────────── */
async function nameEncoding(browser, errs) {
  console.log('\n── 이름 감싸기 ──');
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push('이름: ' + e.message));
  await page.goto(U, { waitUntil: 'networkidle' });

  const round = await page.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-1'), sel2 = {};
    for (let q = 1; q <= ex.nQ; q++) sel2[q] = 1;
    const h = hashStrFinal(ex, sel2, '홍길동', 'A12');
    return { plain: h.includes('홍길동'), back: decName(h.split('.').pop()),
             legacy: decName(encodeURIComponent('김철수')), latin: decName(encName('Eric Cho')) };
  });
  chk('이름이 평문으로 안 들어감', round.plain, false);
  chk('되읽으면 원래 이름', round.back, '홍길동');
  chk('예전 링크(퍼센트 인코딩)도 읽힘', round.legacy, '김철수');
  chk('영문 이름도 왕복', round.latin, 'Eric Cho');

  const link = await page.evaluate(() => {
    const ex = FINAL_EXAMS.find(e => e.id === 'jmchc-1'), sel2 = {};
    for (let q = 1; q <= ex.nQ; q++) sel2[q] = ex.key[q - 1];
    return shareLinkFinal(ex, sel2, '홍길동', 'A12');
  });
  chk('공유 링크에도 이름이 안 보임', link.includes('홍길동'), false);
  await page.close();

  const opened = await browser.newPage();
  opened.on('pageerror', e => errs.push('열기: ' + e.message));
  await opened.goto(link, { waitUntil: 'networkidle' });
  await opened.waitForTimeout(2000);
  // scoreAuto() 가 app.innerHTML 을 통째로 바꾸므로 #nm 은 이미 없다.
  // 성적표에 이름이 실제로 실렸는지를 본다.
  const shown = await opened.evaluate(() => ({
    name: (window.__rpt || {}).name || '',
    inBody: document.body.innerText.includes('홍길동'),
  }));
  chk('링크를 열면 이름 복원', shown.name, '홍길동');
  chk('성적표 본문에 이름이 나온다', shown.inBody, true);
  await opened.close();
}


/* ── 4부. 영역 레이더 · 공유 화면 정리 ─────────────────────────────── */
async function radarAndSharedUI(browser, errs) {
  console.log('\n── 영역 레이더 · 공유 화면 ──');
  const teacher = await browser.newPage();
  teacher.on('pageerror', e => errs.push('교사: ' + e.message));
  await teacher.goto(U, { waitUntil: 'networkidle' });
  await teacher.waitForTimeout(700);
  const made = await teacher.evaluate(async () => {
    localStorage.clear();
    openExam('jmchc-4');
    document.getElementById('nm').value = '오승민';
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      setAns(q, acc[0] || 1);
    }
    for (let q = 1; q <= cur.nQ; q += 3) setAns(q, (cur.key[q - 1] % 4) + 1);
    scoreAuto();
    await new Promise(r => setTimeout(r, 2500));
    const svg = [].slice.call(document.querySelectorAll('.sec svg')).find(s => s.querySelector('polygon'));
    // `.barrow` 는 '개념(유형) 숙련도' 섹션에서도 쓰인다. 레이더가 들어 있는
    // '영역별 성취' 섹션 안에서만 세야 축 수와 견줄 수 있다.
    const sec = svg ? svg.closest('.sec') : null;
    const bars = new Set(sec ? [].slice.call(sec.querySelectorAll('.barrow .ba')).map(e => e.textContent) : []);
    return { axes: svg ? svg.querySelectorAll('text').length : 0,
             bars: bars.size,
             nextStudent: document.body.innerText.includes('다음 학생 입력'),
             link: shareLinkFinal(cur, sel, '오승민', '') };
  });
  console.log(`  레이더 축 ${made.axes} · 아래 막대 영역 ${made.bars}`);
  // 대분류로 접으면 1단원 시험은 축이 3개로 줄어 삼각형이 된다. 세부 영역으로
  // 그리므로 축이 넉넉히 나와야 한다(최대 14로 자른다).
  chk('레이더 축이 3개보다 많다', made.axes > 3, true);
  chk('레이더 축 수가 막대 영역 수와 맞는다(최대 14)', made.axes, Math.min(14, made.bars));
  chk('교사 화면에는 다음 학생 입력이 있다', made.nextStudent, true);
  await teacher.close();

  const shared = await browser.newPage();
  shared.on('pageerror', e => errs.push('공유: ' + e.message));
  await shared.goto(made.link, { waitUntil: 'networkidle' });
  await shared.waitForTimeout(2500);
  const seen = await shared.evaluate(() => ({
    nextStudent: document.body.innerText.includes('다음 학생 입력'),
    regrade: document.body.innerText.includes('다시 채점'),
    retest: document.body.innerText.includes('동형 미니 시험지 인쇄'),
    word: document.body.innerText.includes('성적표 Word 저장'),
    name: (window.__rpt || {}).name || '',
  }));
  // 학부모·학생이 보는 화면에 채점자용 버튼이 있으면 눌러서 성적표를 잃는다
  chk('공유 화면에는 다음 학생 입력이 없다', seen.nextStudent, false);
  chk('공유 화면에는 다시 채점도 없다', seen.regrade, false);
  chk('시험지 인쇄는 그대로 둔다', seen.retest, true);
  chk('Word 저장도 그대로 둔다', seen.word, true);
  chk('성적표 자체는 정상', seen.name, '오승민');
  await shared.close();
}

(async () => {
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  /* ⚠ 브라우저에 건다 — 화면 하나에 걸면 나중에 여는 화면이 샌다. */
  await noSheet(browser);
  const errs = [];
  await cohortSnapshot(browser, errs);
  await legacySnapshot(browser, errs);
  await yearRankSnapshot(browser, errs);
  await nameEncoding(browser, errs);
  await radarAndSharedUI(browser, errs);
  /* ⚠ 화면 하나에만 막으면 샌다. 이 검사는 화면을 여섯 장 여는데(선생님·학부모·
     공유…), 처음 한 장에만 걸었더니 나머지가 그대로 운영 시트로 나갔다 —
     CI 가 "__fsheet… is not defined" 로 죽었다(콜백을 지운 뒤에 진짜 응답이
     도착한 것이다). 가로챈 횟수가 0 이면 아무것도 안 막힌 것이다. */
  console.log('  가로챈 시트 요청 ' + noSheet.seen.n + '건 · ' + JSON.stringify(noSheet.seen.hosts));
  chk('운영 시트로 안 나간다', noSheet.seen.n > 0, true);
  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
