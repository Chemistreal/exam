/* ============================================================
   **회차 주소를 한자리에 모은다** — 눈으로 본 것이 손에 들어온다 (브라우저 필요)
   ------------------------------------------------------------
   2026-08-13, 선생님 요청 — *"시험명 · 제출주소를 모두 모아서 한번에 적어줘.
   페이지 맨밑에 원클릭으로 복붙할 수 있게."*

   회차마다 「제출 링크 ⧉」 는 진작에 있었다. 다만 서른아홉 개를 한 번에 어디다
   적으려면 **서른아홉 번 눌러 서른아홉 번 붙여야 했다.** 공지 하나 쓰는 데.

   여기서 지키는 것
   ----------------
     · **한 회차도 안 빠진다** — 빠진 회차는 그 반 학생이 못 낸다는 뜻이다
     · **보이는 그대로 복사된다** — 눈으로 본 것과 손에 들어온 것이 다르면
       선생님은 붙여 넣고 나서야 안다
     · **학생이 열 수 있는 주소**다 — 내 컴퓨터에서 열어 복사하면 `localhost`
       가 딸려 가고, 받은 학생은 아무 데도 못 간다
     · 회차 카드의 「제출 링크」 와 **같은 주소**다 — 두 자리가 갈리면 같은
       회차가 두 주소를 갖는다

   ⚠ 이 검사는 **주소가 실제로 열리는지 안 본다.** 그것은 망을 타는 일이고
     `tests/page-health.js` 가 보는 자리다. 여기서 보는 것은 «선생님 손에
     들어오는 글» 이다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/submit-links.js
   ============================================================ */
'use strict';
const path = require('path');
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH;
const ROOT = path.join(__dirname, '..');
let PORT = Number(process.env.PORT || 0);

let fail = 0;
const chk = (n, ok, extra) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (extra ? '  ' + extra : ''));
  if (!ok) fail++;
};

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  /* 붙여넣기 자리를 실제로 쓴다 — «복사했다» 는 말만 믿지 않는다. */
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write'],
    { origin: `http://localhost:${PORT}` });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 120)));

  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length
    && !!document.querySelector('#app .card'), null, { timeout: 30000 });

  const nExam = await p.evaluate(() => FINAL_EXAMS.length);
  console.log('── 회차 ' + nExam + '개 ──');

  /* ── ① 맨 밑에 있고, 한 회차도 안 빠진다 ── */
  const box = await p.evaluate(() => {
    const el = document.querySelector('.alink');
    if (!el) return null;
    const cards = document.querySelectorAll('#app .card');
    const last = cards[cards.length - 1];
    return {
      /* 마지막 회차 카드보다 아래에 있는가 — «맨 밑» 이 요청이었다. */
      below: !!last && (el.compareDocumentPosition(last) & Node.DOCUMENT_POSITION_PRECEDING) !== 0,
      text: (document.getElementById('alinkT') || {}).value || '',
      buttons: document.querySelectorAll('.alink__a button').length,
    };
  });
  chk('맨 밑에 칸이 있다', !!box && box.below);
  chk('단추가 한 번에 눌리게 있다', box && box.buttons >= 1, (box && box.buttons) + '개');

  const missing = await p.evaluate(() => {
    const t = (document.getElementById('alinkT') || {}).value || '';
    return FINAL_EXAMS.filter(e => t.indexOf(e.title) < 0 || t.indexOf('exam=' + e.id) < 0)
      .map(e => e.id);
  });
  chk('한 회차도 안 빠졌다', missing.length === 0, missing.join(' ') || '없음');

  /* ── ② 보이는 그대로가 복사된다 ── */
  console.log('\n── 눈으로 본 것과 손에 들어온 것 ──');
  for (const fmt of ['list', 'tsv']) {
    await p.evaluate(f => copyAllLinks(f), fmt);
    await p.waitForTimeout(300);
    const r = await p.evaluate(async () => ({
      shown: (document.getElementById('alinkT') || {}).value || '',
      held: await navigator.clipboard.readText(),
    }));
    chk((fmt === 'tsv' ? '표' : '목록') + ' — 화면 글과 복사된 글이 같다',
      r.shown === r.held && r.held.length > 100,
      r.held.length + '자');
    if (fmt === 'tsv') {
      const lines = r.held.split('\n');
      chk('표는 회차 수만큼 줄이다', lines.length === nExam, lines.length + '줄');
      chk('표는 시험명⇥주소 두 칸이다',
        lines.every(l => l.split('\t').length === 2), lines[0]);
    } else {
      chk('목록은 시험명 다음 줄에 주소가 온다',
        /\n?JMChC 모의고사 1회\nhttps?:\/\/\S+exam=jmchc-1\n/.test('\n' + r.held + '\n'),
        r.held.split('\n').slice(1, 3).join(' ⏎ '));
    }
  }

  /* ── ③ 학생이 열 수 있는 주소인가 ── */
  console.log('\n── 학생이 열 수 있는 주소 ──');
  const local = await p.evaluate(() => ({
    base: siteBase(),
    here: siteBaseIsHere(),
    said: (document.querySelector('.alink__s') || {}).textContent || '',
  }));
  /* 지금은 localhost 에서 보고 있다 — 그러면 배포 주소로 적고 **그렇다고
     말해야** 한다. 말없이 바꾸면 선생님은 왜 주소가 다른지 모른다. */
  chk('localhost 를 학생에게 안 넘긴다', !/localhost|127\.0\.0\.1/.test(local.base), local.base);
  chk('주소를 바꿨다고 말한다', !local.here && /실제 배포 주소/.test(local.said),
    local.said.replace(/\s+/g, ' ').slice(-70));

  /* ── ④ 회차 카드의 단추와 같은 주소인가 ── */
  console.log('\n── 두 자리가 같은 주소를 말한다 ──');
  const same = await p.evaluate(async () => {
    const id = FINAL_EXAMS[0].id;
    copyStudentLink(id);
    await new Promise(r => setTimeout(r, 250));
    const one = await navigator.clipboard.readText();
    const t = allLinksText('tsv').split('\n')
      .find(l => l.indexOf('exam=' + encodeURIComponent(id)) > 0) || '';
    return { one: one, inList: t.split('\t')[1] || '' };
  });
  chk('카드 단추와 맨 밑 목록이 같은 주소다', same.one === same.inList && !!same.one,
    same.one + (same.one === same.inList ? '' : ' ≠ ' + same.inList));

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n서른아홉 개를 한 번에 가져갈 수 있고, 본 것이 그대로 손에 들어온다.');
  process.exit(fail ? 1 : 0);
})();
