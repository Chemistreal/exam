/* ============================================================
   답안을 치는 중에 화면이 갈아엎히거나 저절로 저장되지 않는가
   (브라우저가 필요하다. ⚠ 예전에는 여기 'CI 에서는 건너뛴다' 고 적혀 있었는데
    2026-08-10 부터 **판에서도 실제로 돈다** — 판 전체 env 에 REQUIRE_BROWSER=1
    이 걸려 있어 playwright 가 없으면 건너뛰지 않고 빨간불이다)
   ------------------------------------------------------------
   2026-08-06, 선생님 말씀.

       "성적을 입력하는 중에 갑자기 자동 저장되어버리거나 화면이 위로 확
        다시 가버리는 등 입력 단계에서 오류가 발생하고, 스프레드시트에는
        학생 기록이 생겼다가 지워졌다가 반복되는 오류가 생겨."

   뿌리는 하나다 — **시트에서 늦게 오는 답이 화면을 다시 그린다.** 채점할 때
   두 가지를 묻는데(인원 loadLiveCohort · 전 회차 이력 loadHist), 둘 다 답이
   몇 초 뒤에 온다. 그 사이 선생님은 '다음 학생' 으로 넘어가 답안을 치고 있다.

       loadLiveCohort(id, function(){ scoreAuto(); });   // ← 저장까지 한다
       loadHist(nm) → rerenderReport() → scoreAuto(true) // ← 화면만 갈아엎는다

   그래서

     · 반쯤 친 답안이 그대로 채점되어 시트로 갔다      → 갑자기 자동 저장
     · 입력칸이 성적표로 갈아엎어졌다                  → 화면이 위로 확 감
     · 그 저장이 2.5초 뒤 인원 재조회를 또 예약하고,
       그 답이 다시 scoreAuto() 를 불렀다              → 스스로 자라는 고리
     · 반쯤 친 답안이 조금씩 달라 줄이 쌓였고, 우연히
       같아진 줄은 재계산의 중복 지우기에 지워졌다     → 생겼다 지워졌다 반복

   앞엣것은 인자 없는 scoreAuto 라 **채점해서 저장하고 시트로 보내는 길**이고,
   뒤엣것은 저장은 안 하지만 성적표로 갈아엎으면서 **스크롤을 맨 위로** 보낸다
   (scoreAuto 끝에 window.scrollTo(0,0)). 둘 다 '성적표가 화면에 없으면 그리지
   않는다' 로 막는다.

   여기서 지키는 것:
   - 인원이 도착해도 **입력 화면은 그대로**다(칸도, 친 답도, 스크롤도)
   - 인원이 도착해도 **시트로 아무것도 안 보낸다**
   - 채점한 뒤 성적표에서는 인원이 도착하면 다시 그린다(그게 이 창구의 목적)
   - 채점 한 번에 시트 전송도 한 번이다(2.5초 뒤 재조회가 한 번 더 보내면 안 된다)
   - **이력**이 도착해도 입력 화면과 스크롤이 그대로다
   - 성적표를 보고 있을 때는 이력이 오면 여전히 다시 그린다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/grading-input.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const BASE = `http://localhost:${PORT}/final.html`;

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
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

const EXAM = 'jmchc-6';

(async () => {
  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));

  /* 시트로 나가는 것을 우리가 받는다. seal 뒤에 걸어야 우리 것이 먼저 맞는다.
     - POST(채점 전송)는 세기만 하고 막는다
     - action=cohort 는 **진짜처럼 대답한다** — 그 답이 도착하는 순간이
       이 검사가 보려는 바로 그 순간이다 */
  let posts = 0, cohortAsks = 0, histAsks = 0;
  /* 이력 응답은 **우리가 부를 때** 오게 한다. 채점하는 순간 나가서 몇 초 뒤에
     오는 것이 진짜 모습이라, 그 '몇 초 뒤' 를 검사가 정해야 한다. */
  let histReply = null;
  await page.route('**://script.google.com/**', route => {
    const req = route.request();
    if (req.method() === 'POST') { posts++; return route.abort('blockedbyclient'); }
    const url = req.url();
    const m = /[?&]callback=([A-Za-z0-9_]+)/.exec(url);
    if (/action=cohort/.test(url) && m) {
      cohortAsks++;
      const body = `${m[1]}({"ok":true,"exam":"${EXAM}","hist":{"30":2,"40":3},"n":5,` +
                   `"yhist":{"30":2,"40":3},"yn":5,"year":2026,"skipped":0});`;
      return route.fulfill({ status: 200, contentType: 'text/javascript', body });
    }
    if (/action=history/.test(url) && m) {
      histAsks++;
      histReply = () => route.fulfill({ status: 200, contentType: 'text/javascript',
        body: `${m[1]}({"ok":true,"rows":[{"examId":"${EXAM}","exam":"JMChC 모의고사 6회",` +
              `"name":"홍길동","school":"","grade":"","answers":"${'1'.repeat(60)}","ts":1700000000000}]});` });
      return;                                  // 붙잡아 둔다 — 우리가 놓아 줄 때 간다
    }
    return route.abort('blockedbyclient');
  });

  await page.goto(BASE, { waitUntil: 'networkidle' });
  /* 시험 목록·기준 기록을 받아 올 때까지 기다린다. 바로 openExam 을 부르면
     FINAL_EXAMS 가 아직 없어 엉뚱한 곳에서 넘어진다. */
  /* `let FINAL_EXAMS` 는 window 의 값이 아니다 — 이름 그대로 봐야 보인다. */
  await page.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
                             null, { timeout: 30000 });
  await page.evaluate(() => localStorage.clear());

  console.log('── 답안을 치는 중에 인원이 도착한다 ──');
  await page.evaluate((id) => { openExam(id); }, EXAM);
  await page.waitForTimeout(100);
  /* 앞 다섯 문항을 친다. 아직 채점을 누르지 않았다.
     결함이 살아 있으면 치는 도중에 칸이 사라진다 — 30초를 기다렸다 넘어지면
     무엇이 잘못됐는지 안 보이니, 그 자리에서 이름을 붙여 실패로 적는다. */
  try {
    /* 처음 그려지는 것은 기다려 준다 — 그것과 '치는 도중에 사라졌다' 는 다르다. */
    await page.waitForSelector('#ai_1', { timeout: 15000 });
    for (let q = 1; q <= 5; q++) {
      await page.fill('#ai_' + q, '', { timeout: 5000 });
      await page.type('#ai_' + q, String((q % 4) + 1));
    }
  } catch (e) {
    console.log('  진단 화면:', (await page.evaluate(() => document.getElementById('app').innerHTML.slice(0, 300))));
    console.log('  진단 오류:', JSON.stringify(errs));
    chk('치는 동안 입력칸이 안 사라진다', String(e.message).split('\n')[0], '(안 사라짐)');
    console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
    await browser.close();
    process.exit(1);
  }
  await page.fill('#nm', '홍길동');
  /* 화면을 조금 내려 둔다 — '위로 확 가버린다' 를 눈으로 보는 자리다. */
  await page.evaluate(() => window.scrollTo(0, 400));
  const scrollBefore = await page.evaluate(() => window.scrollY);
  const postsBefore = posts;

  /* 인원 응답이 도착할 시간을 준다(라우트는 즉시 답하지만 script 붙는 시간). */
  await page.waitForTimeout(1200);

  chk('인원을 묻긴 했다', cohortAsks > 0, true);
  chk('입력칸이 그대로 있다', await page.evaluate(() => !!document.getElementById('ai_1')), true);
  chk('성적표로 갈아엎히지 않았다',
    await page.evaluate(() => !!document.getElementById('repPDF')), false);
  chk('친 답이 남아 있다',
    await page.evaluate(() => [1, 2, 3, 4, 5].map(q => document.getElementById('ai_' + q).value)),
    ['2', '3', '4', '1', '2']);
  chk('이름도 남아 있다', await page.evaluate(() => document.getElementById('nm').value), '홍길동');
  chk('화면이 위로 안 갔다', await page.evaluate(() => window.scrollY), scrollBefore);
  chk('시트로 아무것도 안 보냈다', posts - postsBefore, 0);
  chk('이 브라우저에도 기록이 안 쌓였다',
    await page.evaluate((id) => subs(id).length, EXAM), 0);

  console.log('\n── 채점하면 그때 한 번 보낸다 ──');
  /* 나머지를 다 채우고 채점한다. */
  await page.evaluate(() => {
    for (let q = 1; q <= cur.nQ; q++) setAns(q, (q % 4) + 1);
    updateProg();
  });
  const postsBeforeScore = posts;
  await page.evaluate(() => scoreAuto());
  await page.waitForTimeout(300);
  chk('성적표가 떴다', await page.evaluate(() => !!document.getElementById('repPDF')), true);
  chk('시트로 한 번 갔다', posts - postsBeforeScore, 1);
  chk('기록이 한 줄 쌓였다', await page.evaluate((id) => subs(id).length, EXAM), 1);

  console.log('\n── 2.5초 뒤 인원 재조회가 또 보내지 않는다 ──');
  /* 저장 뒤에는 인원을 다시 묻는다(한 명 늘었으니). 그 답이 와도 **다시 그리기만**
     해야 한다 — 예전에는 그 답이 scoreAuto() 를 불러 같은 채점을 또 보냈다. */
  const postsAfterScore = posts;
  await page.waitForTimeout(4000);
  chk('한 번 더 보내지 않았다', posts - postsAfterScore, 0);
  chk('줄이 늘지 않았다', await page.evaluate((id) => subs(id).length, EXAM), 1);
  chk('성적표는 그대로 보인다', await page.evaluate(() => !!document.getElementById('repPDF')), true);
  /* 다시 그렸다면 새 인원(5명)이 성적표에 반영돼 있어야 한다 — 이 창구의 목적이다. */
  chk('새 인원으로 다시 그렸다',
    await page.evaluate(() => (LIVE_POOL && LIVE_POOL.n) || 0), 5);

  console.log('\n── 다음 학생을 치는 중에 앞 학생의 인원 답이 도착한다 ──');
  /* 실제로 선생님이 겪은 차례다. 채점 → 다음 학생 → 치는 중에 답 도착. */
  await page.evaluate(() => { nextStudent(); });
  await page.waitForTimeout(100);
  for (let q = 1; q <= 3; q++) { await page.fill('#ai_' + q, ''); await page.type('#ai_' + q, '1'); }
  const postsB = posts, subsB = await page.evaluate((id) => subs(id).length, EXAM);
  /* 인원 재조회를 강제로 한 번 더 일으키고(캐시를 비운다) 답이 오게 둔다. */
  await page.evaluate((id) => { LIVE_ASK[id] = 0; LIVE_POOL = null; loadLiveCohort(id, cohortRedraw); }, EXAM);
  await page.waitForTimeout(1200);
  chk('입력칸이 그대로 있다', await page.evaluate(() => !!document.getElementById('ai_1')), true);
  chk('친 답이 남아 있다',
    await page.evaluate(() => [1, 2, 3].map(q => document.getElementById('ai_' + q).value)),
    ['1', '1', '1']);
  chk('시트로 안 보냈다', posts - postsB, 0);
  chk('줄이 안 늘었다', (await page.evaluate((id) => subs(id).length, EXAM)) - subsB, 0);

  console.log('\n── 다음 학생을 치는 중에 앞 학생의 이력 답이 도착한다 ──');
  /* 채점할 때 인원 말고 **전 회차 이력**도 같이 물어 본다(loadHist). 그 답도
     성적표를 다시 그린다 — 저장은 안 하지만 화면을 갈아엎고 **스크롤을 맨 위로**
     보낸다(scoreAuto 끝에 window.scrollTo(0,0)). 그것이 "입력할 때 스크롤이
     저절로 이동하던" 나머지 한 갈래다. */
  chk('이력을 묻긴 했다', histAsks > 0, true);
  await page.evaluate(() => window.scrollTo(0, 400));
  const scrollB = await page.evaluate(() => window.scrollY);
  if (histReply) { await histReply(); histReply = null; }
  await page.waitForTimeout(1200);
  chk('입력칸이 그대로 있다', await page.evaluate(() => !!document.getElementById('ai_1')), true);
  chk('성적표로 갈아엎히지 않았다',
    await page.evaluate(() => !!document.getElementById('repPDF')), false);
  chk('스크롤이 안 튀었다', await page.evaluate(() => window.scrollY), scrollB);
  chk('친 답이 남아 있다',
    /* 칸이 사라졌으면 여기서 넘어지지 않고 무엇이 없어졌는지 적는다 —
       실패가 예외로 바뀌면 뒤 검사가 통째로 안 돈다. */
    await page.evaluate(() => [1, 2, 3].map(q => {
      const el = document.getElementById('ai_' + q); return el ? el.value : '(칸이 없다)';
    })),
    ['1', '1', '1']);

  console.log('\n── 성적표를 보고 있을 때는 이력이 오면 다시 그린다 ──');
  /* 막기만 하면 안 된다 — 성적표 위에서는 '지금까지 N회 응시' 가 이력이 와야
     맞는다. 그 자리에서는 여전히 다시 그려야 한다. */
  await page.evaluate(() => {
    for (let q = 1; q <= cur.nQ; q++) setAns(q, (q % 4) + 1);
    document.getElementById('nm').value = '홍길동';
    scoreAuto(true);                       // 저장 없이 성적표만 띄운다
  });
  await page.waitForTimeout(200);
  const marked = await page.evaluate(() => {
    HIST_ROWS = [{ examId: 'zzz', exam: '다른 회차', name: '홍길동', answers: '1', ts: 1 }];
    HIST_FOR = '홍길동';
    const before = document.getElementById('repPDF') && document.getElementById('repPDF').dataset.t;
    document.getElementById('repPDF').dataset.t = 'old';
    rerenderReport();
    return { was: before, now: document.getElementById('repPDF').dataset.t };
  });
  chk('성적표 위에서는 다시 그린다', marked.now, undefined);

  chk('자바스크립트 오류 없음', errs, []);
  await browser.close();
  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})();
