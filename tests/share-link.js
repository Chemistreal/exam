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
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const U = `http://localhost:${PORT}/final.html`;

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) { console.log('건너뜀: playwright 를 찾지 못했다 (PLAYWRIGHT_MODULE 로 경로 지정)'); process.exit(0); }

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
    return { N: cs.N, ready: cs.percReady, qp0: cs.qp && cs.qp[0], qopt0: cs.qopt && cs.qopt[0],
             disc0: cs.qdisc && cs.qdisc[0], totals: cs.totals.slice().sort((a, b) => a - b),
             link: shareLinkFinal(ex, sel2, '홍길동', '') };
  });
  console.log(`  교사 쪽: N=${made.N} 1번 정답률=${made.qp0} · 링크 ${made.link.length}자`);
  chk('교사 쪽 또래 통계 활성', made.ready, true);
  chk('링크에 s= 스냅숏이 들어감', /#s=[A-Za-z0-9_-]+&r=/.test(made.link), true);
  chk('링크 길이가 2000자 미만', made.link.length < 2000, true);
  await teacher.close();

  // 학부모 브라우저: 누적 기록이 하나도 없다
  const parent = await browser.newPage();
  parent.on('pageerror', e => errs.push('학부모: ' + e.message));
  await parent.goto(made.link, { waitUntil: 'networkidle' });
  await parent.waitForTimeout(2500);
  const seen = await parent.evaluate(() => {
    const cs = cohortStats(FINAL_EXAMS.find(e => e.id === 'hwol-2018'));
    return { N: cs.N, ready: cs.percReady, fromLink: !!cs.fromLink,
             qp0: cs.qp && cs.qp[0], qopt0: cs.qopt && cs.qopt[0], disc0: cs.qdisc && cs.qdisc[0],
             totals: cs.totals.slice().sort((a, b) => a - b),
             peerText: document.body.innerText.includes('또래') };
  });
  chk('학부모 쪽에도 또래 통계가 뜬다', seen.ready, true);
  chk('링크에서 온 것으로 표시', seen.fromLink, true);
  chk('인원수 그대로', seen.N, made.N);
  chk('1번 정답률 그대로', seen.qp0, made.qp0);
  chk('1번 선택 분포 그대로', seen.qopt0, made.qopt0);
  chk('1번 변별도 그대로', seen.disc0, made.disc0);
  chk('점수 분포 그대로(백분위 계산용)', seen.totals, made.totals);
  chk('화면에 또래 문구가 나온다', seen.peerText, true);
  await parent.close();
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
  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });
  const errs = [];
  await cohortSnapshot(browser, errs);
  await nameEncoding(browser, errs);
  await radarAndSharedUI(browser, errs);
  chk('JS 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
