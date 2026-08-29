/* ============================================================
   성적표가 **사람에게 어떻게 말하는가**
   ------------------------------------------------------------
   2026-08-10, 선생님 말씀.

       "실사용자 입장에서 경험해보고 개선해야할점을 찾아보라고 했더니
        기술적인 것만 네가 접근하는 경향이 있는거같아 인문학적으로도 접근해줘"

   26/60 을 맞은 학생의 성적표를 화면으로 그려서 문장만 읽었더니 여섯이
   걸렸다(`docs/성적표를-읽는-사람.md`). 선생님이 여섯을 다 정하셨다 —
   *"B10~15 모두 적절한 방향으로 수정"*.

   ⚠ 이 검사는 **글의 좋고 나쁨을 안 본다.** 그건 사람이 본다.
     정해 둔 여섯 가지가 **되돌아가지 않는지**만 본다.

       B10  '수상권 밖' 을 한 화면에서 두 번 말하지 않는다
       B11  수상권 밖이면 길이 큰 글씨, 위치는 작은 딱지 —
            **수상권 안이면 등급이 그대로 큰 글씨다**(빼앗지 않는다)
       B12  학부모께 하는 말이 **부탁으로 시작**한다(판정은 그 다음)
       B13  확률 0% 에 **시점**이 붙는다 — 숫자는 안 바꾼다
       B14  이름이 없으면 사람을 주어로 삼지 않는다
       B15  무응답이 많으면 **어디에 몰렸는지**로 뜻을 말한다

   ⚠ 숫자가 그대로인지도 같이 본다. 말을 다듬다 숫자가 바뀌면 그건 고침이
     아니라 사고다 — 등급·정답 수·석차가 그대로 나오는지 확인한다.

   실행:
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/report-voice.js
   ============================================================ */
'use strict';
const noSheet = require('./_nosheet.js');
require('./_watchdog.js')(180);

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const PORT = Number(process.env.PORT || 8931);

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
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] },
    process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}));
  /* ⚠ **시트를 막고 시작한다**(2026-08-12). 이 검사는 `DT/**` 만 막고 있어서
     학원의 진짜 시트를 그대로 읽고 있었다 — 채점하는 자리는 거기에 줄까지
     쓴다. `tests/_nosheet.js` 는 그 일을 막으려고 진작에 만들어 둔 자인데
     여기 안 걸려 있었다. 걸지 않은 자는 없는 자와 같다. */
  await noSheet(browser);
  const ctx = await browser.newContext({ serviceWorkers: 'block' });
  await ctx.route('**://script.google.com/**', r => r.abort());
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'load', timeout: 40000 });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length,
    null, { timeout: 30000 });

  const r = await p.evaluate(() => {
    const eid = 'hwol-2017';
    const ex = FINAL_EXAMS.find(e => e.id === eid);
    openExam(eid);
    const text = h => { const d = document.createElement('div'); d.innerHTML = h || '';
      return (d.innerText || d.textContent || '').replace(/\s+/g, ' ').trim(); };

    /* ① 아래쪽 학생 — 26문항 정답, 뒤쪽 15문항을 비운다(시간이 모자란 꼴) */
    let ok = 0;
    for (let q = 1; q <= ex.nQ; q++) {
      if (q > 45) { setAns(q, 0); continue; }
      if (ok < 26) { setAns(q, ex.key[q - 1]); ok++; } else setAns(q, (ex.key[q - 1] % 4) + 1);
    }
    window.__fw = [];
    for (let q = 1; q <= ex.nQ; q++) if (!okq(ex, q, sel[q] || 0)) window.__fw.push({ q: q, a: sel[q] || 0 });
    const W = ex.nQ - ok, pct = Math.round(ok / ex.nQ * 100);
    const lowHeroHTML = finalHero('박바다', ex, ok, ex.nQ, W, pct);
    const low = {
      hero: text(lowHeroHTML),
      heroLead: /fhero__head--lead/.test(lowHeroHTML),
      heroChip: /fhero__now/.test(lowHeroHTML),
      heroTier: /fhero__tier/.test(lowHeroHTML),
      parent: text(parentNoteFinal('박바다', ex, ok, ex.nQ, W, pct)),
      prob: text(winProbSec(ex, sel, cohortStats(ex), ok, ex.nQ, W)),
      correct: ok, tier: award(W, effCut(ex)).name
    };
    const noName = (() => { const o = curName; window.curName = () => '';
      const h = text(narrativeSec(ex, sel)); window.curName = o; return h; })();

    /* ② 위쪽 학생 — 거의 다 맞힌다. 등급은 그대로 큰 글씨여야 한다 */
    let ok2 = 0;
    for (let q = 1; q <= ex.nQ; q++) { setAns(q, q <= ex.nQ - 2 ? ex.key[q - 1] : (ex.key[q - 1] % 4) + 1); }
    for (let q = 1; q <= ex.nQ; q++) if (okq(ex, q, sel[q] || 0)) ok2++;
    const W2 = ex.nQ - ok2;
    const hiHTML = finalHero('상위권', ex, ok2, ex.nQ, W2, Math.round(ok2 / ex.nQ * 100));
    const hi = { tier: /fhero__tier/.test(hiHTML), lead: /fhero__head--lead/.test(hiHTML),
                 name: award(W2, effCut(ex)).name, inA: award(W2, effCut(ex)).inA };
    return { low: low, noName: noName, hi: hi };
  });

  console.log('\n── 수상권 밖 학생 ──');
  console.log('  히어로: ' + r.low.hero.slice(0, 90));

  // B10 · B11
  const outCount = (r.low.hero.match(/수상권 밖/g) || []).length;
  chk('B10 · 히어로가 "수상권 밖" 을 한 번만 말한다', outCount <= 1, `(${outCount}번)`);
  chk('B11 · 수상권 밖이면 길이 큰 글씨다', r.low.heroLead && r.low.heroChip && !r.low.heroTier, true);
  /* ⚠ 2026-08-29 에 **이름이 바뀌었다.** '수상권 밖' → '장려상 도전권'
     (컷에서 5문항 이내면 '장려상 수상권 근처'). 선생님 결정이다 — 어디에
     없는지가 아니라 어디로 가는지로 부른다.

     여기서 지키는 것은 **낱말이 아니라 원칙**이다: 장려 컷 아래인 학생에게
     그 사실을 숨기지 않는다. 그래서 새 이름 중 하나가 반드시 보여야 한다.
     낱말로 박아 두면 이름이 또 바뀔 때 좋은 변화가 검사를 깨뜨린다. */
  chk('B11 · 그래도 위치를 숨기지 않는다',
      /장려상 도전권|장려상 수상권 근처/.test(r.low.hero), true);
  chk('B11 · 수상권 안이면 등급이 그대로 큰 글씨다',
    r.hi.inA ? (r.hi.tier && !r.hi.lead) : true, true, );

  // B12
  console.log('\n  학부모: ' + r.low.parent.slice(0, 80));
  const iAsk = r.low.parent.indexOf('다시 풀어오는 과정');
  const iVerdict = r.low.parent.indexOf('에 해당합니다');
  chk('B12 · 학부모께 하는 말이 부탁으로 시작한다',
    iAsk >= 0 && iVerdict >= 0 && iAsk < iVerdict, `(부탁 ${iAsk} · 판정 ${iVerdict})`);
  chk('B12 · 판정을 빼지는 않았다', iVerdict >= 0, true);

  // B13
  const zeroBare = /확률 0%/.test(r.low.prob.replace(/아직 /g, '@'));
  chk('B13 · 0% 에 시점이 붙는다',
    !/0%/.test(r.low.prob) || /아직 0%/.test(r.low.prob) || /지금 실력 그대로일 때/.test(r.low.prob), true);
  chk('B13 · 0% 면 얼마가 되는지 같이 적는다',
    !/아직 0%/.test(r.low.prob) || /문항.{0,4}회복하면.{0,6}%가 됩니다/.test(r.low.prob), true);

  // B14
  console.log('\n  이름 없을 때: ' + r.noName.slice(0, 60));
  chk('B14 · 이름이 없으면 "학생은" 으로 시작하지 않는다',
    !/^\s*0?1?\s*한눈에 보는 진단\s*학생은/.test(r.noName) && !/ 학생은 이번 진단/.test(r.noName), true);

  // B15
  chk('B15 · 무응답이 많으면 어디에 몰렸는지 말한다',
    /뒤쪽|고르게 흩어/.test(r.low.parent), true);
  chk('B15 · 비운 수를 바르게 센다 (전부로 세지 않는다)', !/비운 60문항/.test(r.low.parent), true);

  // 숫자는 그대로인가
  chk('말을 다듬어도 숫자는 그대로다 (정답 수)',
    new RegExp(r.low.correct + '/60').test(r.low.parent), true);
  chk('말을 다듬어도 숫자는 그대로다 (등급)',
    r.low.parent.indexOf(r.low.tier) >= 0, true);

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;
  await browser.close();
  console.log(fail ? `\n실패 ${fail}건` : '\n정해 둔 여섯 가지를 그대로 지킨다.');
  process.exit(fail ? 1 : 0);
})();
