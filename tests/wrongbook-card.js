/* ============================================================
   오답노트 카드가 학생에게 말해 주는 것들 (브라우저 필요)
   ------------------------------------------------------------
   오답 카드 한 장은 네 가지를 말해야 한다.

     1. 고른 ③이 왜 틀렸나   ← 답지의 `misconceptions[고른번호]`
     2. 이 문항에서 흔한 실수  ← 답지의 `misconception` (누가 풀든 같은 줄)
     3. 개념 보충            ← RX 의 처방 한 줄
     4. 그 개념 강의로 가는 문 ← lecFor(area, type)

   1번과 4번은 오래 비어 있었다. 「왜 틀렸나」는 문항마다 한 줄뿐이라 ②를 고른
   학생과 ④를 고른 학생이 **같은 문장**을 읽었고, 강의 문은 개념 클리닉 절에만
   걸려 있어 정작 틀린 문항을 들여다보는 자리에는 없었다.

   여기서 지키는 것:
   - 답지에 선지별 오개념이 있는 문항을 틀리면 «고른 그 번호» 줄이 선다
   - 무응답이면 그 줄이 서지 않는다 (고른 번호가 없다)
   - 강의 문이 서고, 그 주소가 **실제로 있는 강의 파일**을 가리킨다
   - 두 줄이 같은 말이면 아랫줄을 접는다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/wrongbook-card.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const noSheet = require('./_nosheet.js');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
const U = `http://localhost:${PORT}/final.html`;

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

/* 선지별 오개념이 실제로 들어 있는 회차·문항을 답지에서 찾는다.
   회차를 이름으로 박아 두면, 그 회차의 답지가 바뀌었을 때 검사가
   «없어서 통과» 로 조용히 넘어간다. 자료를 보고 고른다. */
function pickTarget() {
  for (const f of fs.readdirSync(path.join(ROOT, 'answers'))) {
    if (!f.endsWith('.json')) continue;
    const id = f.slice(0, -5);
    const qs = JSON.parse(fs.readFileSync(path.join(ROOT, 'answers', f), 'utf8')).questions || {};
    for (const k of Object.keys(qs).sort((a, b) => a - b)) {
      const mis = qs[k].misconceptions;
      if (mis && Object.keys(mis).length) return { id, q: Number(k), mis };
    }
  }
  return null;
}

(async () => {
  const T = pickTarget();
  if (!T) { console.log('실패: 선지별 오개념이 있는 문항이 답지에 하나도 없다'); process.exit(1); }
  const LECS = new Set(fs.readdirSync(ROOT).filter(x => /^lec-\d+.*\.html$/.test(x)));
  console.log(`대상: ${T.id} ${T.q}번 (선지별 오개념 ${Object.keys(T.mis).join('·')})`);

  const browser = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  await noSheet(browser);
  const page = await browser.newPage();
  await page.setViewportSize({ width: 900, height: 1400 });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));

  await page.goto(U, { waitUntil: 'networkidle' });
  await page.waitForTimeout(700);

  // 대상 문항은 «오개념이 적힌 번호» 로 틀리고, 그다음 문항은 무응답으로 둔다.
  const badPick = Number(Object.keys(T.mis).sort()[0]);
  const blankQ = await page.evaluate(([examId, q, pick]) => {
    localStorage.clear();
    openExam(examId);
    document.getElementById('nm').value = '카드보기';
    for (let i = 1; i <= cur.nQ; i++) {
      const acc = (cur.multi && cur.multi[i]) || [cur.key[i - 1]];
      setAns(i, acc[0] || 1);
    }
    setAns(q, pick);
    const blank = q === cur.nQ ? q - 1 : q + 1;
    setAns(blank, 0);            // 무응답
    scoreAuto();
    return blank;
  }, [T.id, T.q, badPick]);
  await page.waitForTimeout(2500);

  const got = await page.evaluate(([q, blank]) => {
    const card = c => document.querySelector(`.wb-card[data-q="${c}"]`);
    const A = card(q), B = card(blank);
    const pick = A && A.querySelector('.wb-pick');
    const lec = A && A.querySelector('.wb-lec');
    return {
      pickText: pick ? pick.textContent.trim() : '',
      pickHead: pick ? (pick.querySelector('b') || {}).textContent || '' : '',
      lecHref: lec ? lec.getAttribute('href') : '',
      lecText: lec ? lec.textContent.trim() : '',
      blankPick: B ? !!B.querySelector('.wb-pick') : null,
      blankHead: B ? (B.querySelector('.wb-head .wb-first') || {}).textContent || '' : '',
      why: A ? [].slice.call(A.querySelectorAll('.wb-why b')).map(b => b.textContent) : [],
      otext: A ? !!A.querySelector('details.wb-otext') : false,
      stem: A ? ((A.querySelector('.wb-ostem') || {}).textContent || '') : '',
      nCh: A ? A.querySelectorAll('.wb-ochoices li').length : 0,
      mine: A ? ((A.querySelector('.wb-ochoices li.is-mine') || {}).textContent || '') : '',
      key: A ? ((A.querySelector('.wb-ochoices li.is-key') || {}).textContent || '') : '',
    };
  }, [T.q, blankQ]);

  const want = T.mis[String(badPick)].replace(/\s+/g, '');
  chk('고른 번호의 오답 해설이 카드에 선다',
    got.pickText.replace(/\s+/g, '').includes(want), true);
  chk('그 줄이 고른 번호를 이름으로 부른다',
    /고른\s*[①②③④]/.test(got.pickHead), true);
  chk('무응답 문항에는 그 줄이 없다', got.blankPick, false);
  chk('무응답이라고 적혀 있다', /무응답/.test(got.blankHead), true);
  chk('강의 문이 선다', !!got.lecHref, true);
  chk('강의 주소가 실제로 있는 파일이다', LECS.has(got.lecHref), true);
  chk('강의 문이 강의 이름을 부른다', /강의 보기/.test(got.lecText), true);
  chk('아랫줄은 「흔한 실수」로 이름이 갈린다',
    got.why.every(t => !/^왜 틀렸나/.test(t)), true);
  /* 크롭 그림 한 장만으로는 세 가지가 안 된다 — 그림이 못 뜨면 문항을 아예 못 보고,
     크롭이 원본의 그래프·표를 잃은 회차에서는 풀 자료가 없고, 숫자를 옮겨 적을 수 없다.
     답지에 원문이 남은 회차는 글로도 싣는다. */
  chk('원문을 글로도 싣는다', got.otext, true);
  chk('그 글이 비어 있지 않다', got.stem.length > 10, true);
  chk('보기 넷을 함께 싣는다', got.nCh, 4);
  chk('고른 보기에 이름표가 붙는다', /고른 것/.test(got.mine), true);
  chk('정답 보기에 이름표가 붙는다', /정답/.test(got.key), true);
  chk('고른 것과 정답이 서로 다른 보기다', got.mine !== got.key, true);
  chk('JS 오류 없음', errs, []);

  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n결과: 전부 통과');
  process.exit(fail ? 1 : 0);
})();
