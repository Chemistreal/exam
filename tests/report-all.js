/* ============================================================
   전 회차 성적표 회귀 — 38회차를 실제로 채점해 끝까지 그린다
   ------------------------------------------------------------
   낱개 검사는 저마다 한 조각씩만 본다. 그런데 성적표는 시험 데이터·오답
   카드·강의 링크·확률이 한 화면에서 만나는 자리라, 조각이 다 멀쩡해도
   합쳐 놓으면 깨질 수 있다. 회차를 새로 넣을 때 특히 그렇다.

   그래서 여기서는 **모든 회차를 실제로 채점한다.** 아홉 문항에 하나씩 틀리게
   넣고 성적표가 끝까지 나오는지, 틀린 문항의 오개념이 카드에 뜨는지 본다.

   ⚠ 두 가지를 조심해야 한다(둘 다 실제로 헛걸음을 시켰다).
   · 전항정답(multi) 문항은 어떤 답을 넣어도 정답이라 '틀린 문항'이 못 된다.
     빼지 않으면 오개념이 안 뜬다고 잘못 센다.
   · `NaN` 을 그냥 찾으면 **질산 나트륨(NaNO₃)** 이 걸린다. 앞뒤에 글자가
     붙지 않은 것만 본다.

   실행:  node tests/report-all.js
     (정적 서버가 8931 포트에 떠 있어야 한다)
   ============================================================ */
'use strict';
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox'] });
  const ctx = await b.newContext();
  await ctx.route('**://script.google.com/**', r => r.abort('blockedbyclient'));
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  await p.addInitScript(() => { try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {} });
  await p.goto('http://localhost:8931/final.html', { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 30000 });
  const ids = await p.evaluate(() => FINAL_EXAMS.map(e => e.id));
  let bad = 0, tot = 0, om = 0, omShown = 0;
  for (const id of ids) {
    const r = await p.evaluate(async (eid) => {
      const ex = FINAL_EXAMS.find(e => e.id === eid);
      openExam(eid);
      const wrong = [];
      /* 전항정답(multi) 문항은 어떤 답을 넣어도 정답이라 '틀린 문항'이 될 수
         없다. 여기에 넣으면 오개념이 화면에 안 뜬다고 잘못 세게 된다. */
      const multi = ex.multi || {};
      for (let q = 1; q <= ex.nQ; q++) {
        const k = ex.key[q - 1];
        const w = (q % 9 === 0) && !multi[String(q)];
        setAns(q, w ? ((k % 4) + 1) : k); if (w) wrong.push(q);
      }
      document.getElementById('nm').value = '전수점검';
      document.getElementById('sch').value = 'X중';
      document.getElementById('grd').value = '3';
      scoreAuto();
      await new Promise(r => setTimeout(r, 900));
      const a = await (await fetch('answers/' + eid + '.json')).json();
      const t = document.getElementById('app').innerText;
      const lines = wrong.map(q => (a.questions[String(q)] || {}).misconception).filter(Boolean);
      return {
        id: eid, nQ: ex.nQ,
        rep: !!document.getElementById('repPDF'),
        leak: /\bundefined\b|\[object|(?<![A-Za-z])NaN(?![A-Za-z0-9₀-₉])/.test(t),
        clinic: /오답 개념 클리닉|개념 클리닉/.test(t),
        lec: document.querySelectorAll('a[href^="lec-"]').length,
        om: lines.length, omShown: lines.filter(x => t.includes(x)).length,
        chars: t.length,
      };
    }, id);
    tot++; om += r.om; omShown += r.omShown;
    const ok = r.rep && !r.leak && r.clinic && r.om === r.omShown && r.chars > 1500;
    if (!ok) { bad++; console.log('  ✗ ' + JSON.stringify(r)); }
  }
  console.log(`\n회차 ${tot}개 · 문제 있는 회차 ${bad}개`);
  console.log(`틀린 문항의 오개념 ${omShown}/${om} 이 화면에 나옴`);
  console.log(errs.length ? ('JS 오류 ' + errs.length + '건:\n  ' + errs.slice(0, 5).join('\n  ')) : 'JS 오류 없음');
  await b.close();
  process.exit(bad || errs.length ? 1 : 0);
})();
