/* ============================================================
   **시험을 본 뒤 문제지와 해설을 손에 쥐여 준다** (브라우저 필요)
   ------------------------------------------------------------
   2026-08-13, 선생님 요청 — *"각 시험 보고 나서 학생 성적표에 문제 pdf 와
   해설 pdf 를 다운받을 수 있도록 링크를 버튼으로 만들어서 적절한 위치에
   첨부해줘."*

   재어 보니 학생이 시험을 본 뒤 자료를 받을 길이 이랬다.

       final-submit.html 제출 직후   문제 ✗   해설 ✗   ← 학생이 보는 첫 화면
       final.html 성적표             문제 ✗   해설 O   ← 성적표 링크로 여는 화면
       답 넣기 전 화면               문제 O   해설 ✗   (일부러 그렇다)

   **문제지가 두 자리 다 빠져 있었다.** 틀린 문항을 다시 보려면 문제가 있어야
   하는데, 답을 넣던 화면을 떠나는 순간 손에서 사라졌다.

   여기서 지키는 것
   ----------------
     · 채점이 **끝난 뒤** 두 화면 다 문제지와 해설이 있다
     · **답을 넣기 전에는 정답이 안 보인다** — 그 자리로 새면 시험이 아니다
     · **없는 것을 있다고 안 한다** — 해설 PDF 가 없는 회차가 열넷이다.
       그런 회차에 «PDF» 라 적으면 학생은 없는 파일을 누른다
     · 걸린 주소가 **실제로 있는 파일**이다 — 404 를 단추로 만들지 않는다
     · 학부모·학생이 여는 **공유 성적표(#r=)** 에도 있다

   ⚠ 이 검사는 PDF 안을 안 본다. «문제지에 답이 실려 있나» 는
     `tools/pdf_answer_leak.py` 가 보는 자리다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/exam-materials.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const { serve } = require('./_serve.js');
const noSheet = require('./_nosheet.js');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH;
const ROOT = path.join(__dirname, '..');
let PORT = Number(process.env.PORT || 0);

/* 해설 PDF 가 **없는** 회차와 **다 있는** 회차를 하나씩 본다.
   하나만 보면 «PDF 가 없을 때 뭐라고 하나» 를 영영 안 재게 된다. */
const BARE = 'hwol-2018';        // 정답 PDF·해설편 PDF 둘 다 없음
const FULL = 'kmchc-2026-1-simhwa';  // 셋 다 있음

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

const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
const byId = id => EXAMS.filter(e => e.id === id)[0];

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {}));
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  const errs = [];

  /* ── ① 학생이 제출한 **직후** 화면 ─────────────────────────────── */
  console.log('── 학생 · 제출 직후 (' + BARE + ' · 해설 PDF 가 없는 회차) ──');
  const p = await ctx.newPage();
  p.on('pageerror', e => errs.push('submit: ' + String(e).slice(0, 90)));
  await p.goto(`http://localhost:${PORT}/final-submit.html?exam=${BARE}`,
    { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => !!document.getElementById('nm'), null, { timeout: 30000 });

  /* 답을 넣기 **전**에 정답이 손에 들어오면 안 된다. */
  const before = await p.evaluate(() => {
    const a = [].map.call(document.querySelectorAll('a[href]'), x => x.getAttribute('href'));
    return { sol: a.filter(h => /^sol-final-|answer\.pdf$|solution-book/.test(h || '')),
             prob: a.filter(h => /-problem\.pdf$/.test(h || '')).length };
  });
  chk('답을 넣기 전에는 정답·해설이 안 보인다', before.sol.length === 0, before.sol.join(' ') || '없음');
  chk('문제지는 그때도 있다', before.prob > 0, before.prob + '곳');

  await p.evaluate(() => {
    document.getElementById('nm').value = '자료점검';
    document.getElementById('sch').value = 'ㅇㅇ중';
    for (let q = 1; q <= cur.nQ; q++) {
      const el = document.getElementById('a' + q); if (el) { el.value = '1'; onIn(q, el); }
    }
  });
  await p.click('#submit');
  await p.waitForFunction(() => /제출 완료/.test(document.body.textContent || ''),
    null, { timeout: 20000 });

  const stu = await p.evaluate(() => {
    const a = document.querySelector('.assets');
    return { has: !!a,
             links: a ? [].map.call(a.querySelectorAll('a'),
               x => ({ t: x.textContent.trim(), h: x.getAttribute('href') })) : [] };
  });
  chk('제출한 뒤 자료 칸이 있다', stu.has);
  chk('문제지 PDF 를 준다', stu.links.some(l => /-problem\.pdf$/.test(l.h)),
    stu.links.map(l => l.t).join(' / ') || '없음');
  chk('해설로 가는 길을 준다', stu.links.some(l => /^sol-final-/.test(l.h)));
  /* 이 회차는 해설 PDF 가 없다. 없는 것을 «PDF» 라 부르면 학생은 없는 파일을
     누르고, 안 열리는 것이 자기 탓인 줄 안다. */
  chk('없는 해설 PDF 를 있다고 하지 않는다',
    !stu.links.some(l => /PDF/.test(l.t) && /\.html$/.test(l.h)),
    stu.links.map(l => l.t + '→' + l.h).join(' / '));

  /* ── ② 걸어 둔 주소가 실제로 있는 파일인가 ────────────────────── */
  console.log('\n── 걸어 둔 주소가 실제로 있는가 (' + EXAMS.length + '회차 전부) ──');
  const dead = [];
  EXAMS.forEach(e => {
    [e.pdf, e.answerPdf, e.bookPdf, 'sol-final-' + e.id + '.html'].forEach(f => {
      if (f && !fs.existsSync(path.join(ROOT, f))) dead.push(e.id + ':' + f);
    });
  });
  chk('죽은 주소가 없다', dead.length === 0, dead.slice(0, 3).join(' ') || '없음');
  chk('모든 회차에 문제지가 있다',
    EXAMS.every(e => e.pdf), EXAMS.filter(e => !e.pdf).map(e => e.id).join(' ') || '39/39');

  /* ── ③ 선생님 성적표 · 공유 성적표(#r=) ────────────────────────── */
  console.log('\n── 성적표 (' + FULL + ' · PDF 가 다 있는 회차) ──');
  const q = await ctx.newPage();
  q.on('pageerror', e => errs.push('final: ' + String(e).slice(0, 90)));
  await q.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'domcontentloaded', timeout: 40000 });
  if (await q.$('#gateIn')) { await q.fill('#gateIn', '0000'); await q.click('#gateGo'); }
  await q.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length
    && !!document.querySelector('#app .card'), null, { timeout: 30000 });
  await q.evaluate(id => openExam(id), FULL);
  await q.waitForFunction(() => !!document.getElementById('ai_1'), null, { timeout: 20000 });
  await q.evaluate(() => {
    document.getElementById('nm').value = '자료점검';
    document.getElementById('sch').value = 'ㅇㅇ중';
    for (let n = 1; n <= cur.nQ; n++) {
      const el = document.getElementById('ai_' + n);
      if (el && !el.disabled) { el.value = '1'; typeAns(n, el); }
    }
    scoreAuto();
  });
  await q.waitForFunction(() => /시험지 · 해설 내려받기/.test(document.body.textContent || ''),
    null, { timeout: 30000 });

  const rep = await q.evaluate(() => {
    const a = document.querySelector('.assets');
    const tb = document.querySelector('.toolbar');
    const wb = document.querySelector('.wb');
    return {
      links: a ? [].map.call(a.querySelectorAll('a'), x => x.getAttribute('href')) : [],
      /* 같은 링크가 두 자리에 있으면 한쪽만 고쳤을 때 갈린다. */
      alsoInToolbar: tb ? tb.querySelectorAll('a.pdf').length : -1,
      /* 틀린 문항을 짚어 준 **뒤**에 있어야 «이 문항 뭐였지» 에 답이 된다. */
      afterWrongbook: !!(a && wb &&
        (wb.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0),
    };
  });
  chk('문제지 PDF 가 성적표에 있다', rep.links.some(h => /-problem\.pdf$/.test(h)),
    rep.links.join(' ') || '없음');
  chk('공식 정답 PDF 가 있다', rep.links.some(h => /-answer\.pdf$/.test(h)));
  chk('문제편·해설편 PDF 가 있다', rep.links.some(h => /solution-book/.test(h)));
  chk('해설 쪽으로 가는 길이 있다', rep.links.some(h => /^sol-final-/.test(h)));
  chk('오답정리 **뒤**에 있다', rep.afterWrongbook === true);
  chk('아래 단추 줄에 같은 링크가 안 남았다', rep.alsoInToolbar === 0,
    rep.alsoInToolbar + '개');

  console.log('\n── 학부모·학생이 여는 공유 성적표 (#r=) ──');
  const link = await q.evaluate(() => {
    try { return shareLinkFinal(cur, sel, '자료점검', ''); } catch (e) { return null; }
  });
  chk('성적표 링크를 만들 수 있다', !!link);
  if (link) {
    const r = await ctx.newPage();
    r.on('pageerror', e => errs.push('shared: ' + String(e).slice(0, 90)));
    await r.goto(link.replace(/^https?:\/\/[^/]+/, `http://localhost:${PORT}`),
      { waitUntil: 'load', timeout: 40000 });
    await r.waitForFunction(() => /시험지 · 해설 내려받기/.test(document.body.textContent || ''),
      null, { timeout: 30000 }).catch(() => {});
    const sh = await r.evaluate(() => {
      const a = document.querySelector('.assets');
      return { gate: !!document.getElementById('gate'),
               n: a ? a.querySelectorAll('a').length : 0 };
    });
    chk('자물쇠가 안 막는다', sh.gate === false);
    chk('학부모 화면에도 자료가 있다', sh.n >= 4, sh.n + '개');
    await r.close();
  }

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건`
    : '\n시험을 본 뒤 문제지와 해설이 학생 손에 들어온다.');
  process.exit(fail ? 1 : 0);
})();
