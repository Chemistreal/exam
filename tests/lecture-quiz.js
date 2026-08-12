/* ============================================================
   **강의록의 확인 문제** — 학생이 스스로 걸고 넘어가는 자리 (브라우저 필요)
   ------------------------------------------------------------
   2026-08-11, 선생님 결정 #25 — *"강의에 확인 문제가 없는 강이 있다"*.
   재어 보니 «있는 강» 이 아니라 **125강 전부에 없었다.**

   문항이 없어서가 아니었다. `donghyung/` 에 사람이 검수한 2,490문항이 이미
   있었고, 없던 것은 «이 강의는 이 개념» 을 이어 주는 표였다
   (`tools/lecture_map.py`).

   여기서 지키는 것 — **글의 좋고 나쁨은 안 본다.** 그것은 사람이 본다.
   이 검사가 보는 것은 그 자리가 **학생에게 제대로 도는가**다.

     · 처음에는 해설이 **닫혀 있다** — 열려 있으면 학생은 읽고 지나간다
     · 고르면 그때 열리고, **정답과 내가 고른 것이 갈라져 보인다**
     · 두 번 눌러도 안 바뀐다 — 답을 바꿔 가며 정답을 찾아내는 놀이가 안 된다
     · 바깥에서 **아무것도 안 받아 온다** — 글 안에 있어야 오프라인에서 열린다
     · 정답이 **눈에 먼저 안 띈다** — 화면 글에 정답 표시가 미리 없다

   ⚠ 이 검사는 **정답이 맞는지 안 본다.** 문항은 이미 사람이 검수했다
     (`verified: true`). 여기서 다시 채점하면 두 자가 같은 것을 다르게 말한다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/lecture-quiz.js
   ============================================================ */
'use strict';
const path = require('path');
const fs = require('fs');
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
  /* ⚠ **시트를 막고 시작한다.** 안 막으면 검사가 학원의 진짜 시트를 읽고,
     채점하는 검사는 **거기에 줄을 쓴다.** 2026-08-12 에 실제로 그랬다 —
     이 검사가 판을 돌 때마다 «무응답점검·분류점검·자료링크점검» 같은 이름이
     선생님 시트에 쌓이고 있었다(POST 를 세어서 확인했다).
     `tests/_nosheet.js` 머리말이 처음부터 이르던 일이다. */
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 100)));

  /* 확인 문제가 붙은 강의 가운데 셋을 본다 — 첫 강 · 한복판 · 종합 강의.
     종합 강의(영역 전체에서 뽑는 것)가 다른 길로 그려지므로 같이 본다. */
  const pages = fs.readdirSync(ROOT).filter(f => /^lec-\d{3}.*\.html$/.test(f)).sort();
  const withQuiz = pages.filter(f =>
    fs.readFileSync(path.join(ROOT, f), 'utf8').includes('data-lecture-quiz'));
  chk('확인 문제가 붙은 강의가 100강을 넘는다', withQuiz.length > 100, withQuiz.length + '강');

  const targets = [withQuiz[0], withQuiz[Math.floor(withQuiz.length / 2)],
                   withQuiz[withQuiz.length - 1]];

  for (const page of targets) {
    console.log('\n── ' + page + ' ──');
    await p.goto(`http://localhost:${PORT}/${page}`, { waitUntil: 'load', timeout: 40000 });

    /* 바깥에서 받아 오는 것이 없어야 한다. 강의록은 학생이 지하철에서 여는
       화면이라, 한 줄이라도 바깥을 기다리면 흰 종이가 된다. */
    const outside = await p.evaluate(() => {
      const bad = [];
      document.querySelectorAll('[data-lecture-quiz] [src],[data-lecture-quiz] [href]')
        .forEach(el => { const u = el.getAttribute('src') || el.getAttribute('href');
                         if (/^https?:|^\/\//.test(u || '')) bad.push(u); });
      return bad;
    });
    chk('바깥에서 아무것도 안 받아 온다', outside.length === 0, outside.join(' ') || '없음');

    const before = await p.evaluate(() => ({
      q: document.querySelectorAll('.lq__q').length,
      opts: document.querySelectorAll('.lq__opt').length,
      open: [].filter.call(document.querySelectorAll('.lq__why'), w => !w.hidden).length,
      keyMark: document.querySelectorAll('.lq__opt.is-key').length,
      /* 화면에 보이는 글에 «정답 ③» 같은 것이 미리 떠 있으면 안 된다. */
      leaked: [].filter.call(document.querySelectorAll('.lq__ans'),
        e => e.offsetParent !== null).length,
    }));
    chk('문항이 둘 이상 있다', before.q >= 2, before.q + '문항');
    chk('보기가 문항마다 있다', before.opts >= before.q * 3, before.opts + '개');
    chk('처음에는 해설이 닫혀 있다', before.open === 0, before.open + '곳 열림');
    chk('처음에는 정답 표시가 없다', before.keyMark === 0 && before.leaked === 0,
        `표시 ${before.keyMark} · 보이는 정답 ${before.leaked}`);

    /* 일부러 **틀린 보기**를 누른다 — 학생 대부분이 겪는 쪽이다. */
    const after = await p.evaluate(() => {
      const ol = document.querySelector('.lq__opts');
      const key = Number(ol.dataset.ans);
      const opts = [].slice.call(ol.querySelectorAll('.lq__opt'));
      opts.find((o, i) => i + 1 !== key).click();
      const q = ol.closest('.lq__q');
      return {
        open: !q.querySelector('.lq__why').hidden,
        key: ol.querySelectorAll('.is-key').length,
        mine: ol.querySelectorAll('.is-miss').length,
        says: (q.querySelector('.lq__ans') || {}).textContent || '',
        why: (q.querySelector('.lq__why') || {}).textContent.length,
        /* 다른 문항은 아직 닫혀 있어야 한다 — 하나 눌렀다고 다 열리면
           남은 문항을 스스로 풀 기회가 사라진다. */
        others: [].filter.call(document.querySelectorAll('.lq__why'), w => !w.hidden).length,
      };
    });
    chk('고르면 해설이 열린다', after.open === true);
    chk('정답이 어느 것인지 보인다', after.key === 1 && /정답/.test(after.says), after.says.trim());
    chk('내가 고른 것도 갈라져 보인다', after.mine === 1);
    chk('해설에 실제로 글이 있다', after.why > 40, after.why + '자');
    chk('다른 문항은 아직 닫혀 있다', after.others === 1, after.others + '곳 열림');

    /* 다시 눌러도 안 바뀐다 — 답을 갈아 가며 정답을 찾아내면 «확인» 이 아니다. */
    const twice = await p.evaluate(() => {
      const ol = document.querySelector('.lq__opts');
      ol.querySelectorAll('.lq__opt').forEach(o => o.click());
      return { key: ol.querySelectorAll('.is-key').length,
               mine: ol.querySelectorAll('.is-miss').length };
    });
    chk('두 번 눌러도 안 바뀐다', twice.key === 1 && twice.mine === 1,
        `정답 ${twice.key} · 고른 것 ${twice.mine}`);
  }

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;

  await browser.close();
  srv.stop();
  console.log(fail ? `\n실패 ${fail}건` : '\n강의를 듣고 나서 스스로 걸어 볼 자리가 있다.');
  process.exit(fail ? 1 : 0);
})();
