/* ============================================================
   영역별 성취의 **판정 기준**이 화면에 적혀 있는가 · 오답 노트가 유형으로 묶이는가
   ------------------------------------------------------------
   성적표는 영역마다 '강점 / 취약' 을 붙인다. 규칙은 이랬다.

       문항 2개 이상 · 정답률 80% 이상  →  강점
       문항 2개 이상 · 정답률 50% 미만  →  취약
       문항 1개                          →  아무것도 안 붙인다

   마지막 줄이 문제였다. 「분자간인력 1/1 · 100%」 이 아무 딱지도 없이 나오니
   "성취도 100인데 왜 강점이 아니냐" 가 된다(2026-08-10, 선생님이 짚으셨다).
   규칙은 맞다 — 문항 하나로 강점이라 하면 우연이 그대로 판정이 된다. 다만
   **그 규칙이 화면 어디에도 없었다.**

   오답 노트도 문항 번호 순이었다. 같은 유형이 3·17·41번으로 흩어져, 학생이
   "내가 이 유형을 못 하는구나" 를 스스로 이어 붙여야 했다.

   여기서 지키는 것.

     · 판정 기준이 성적표에 글로 적혀 있다
     · 문항 1개인 영역은 **빈칸이 아니라** '판정 안 함' 이라고 말한다
     · 영역마다 어떤 문항이 들어갔는지, 그 문항이 어떤 유형인지 보인다
     · 오답 노트가 유형으로 묶이고, **취약한 유형이 앞에 온다**

   실행:  node tests/area-verdict.js
     (정적 서버가 8931 포트에 떠 있어야 한다)
   ============================================================ */
'use strict';
const noSheet = require('./_nosheet.js');
require('./_watchdog.js')(180);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const PORT = Number(process.env.PORT || 8931);

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  /* ⚠ **시트를 막고 시작한다.** 안 막으면 검사가 학원의 진짜 시트를 읽고,
     채점하는 검사는 **거기에 줄을 쓴다.** 2026-08-12 에 실제로 그랬다 —
     이 검사가 판을 돌 때마다 «무응답점검·분류점검·자료링크점검» 같은 이름이
     선생님 시트에 쌓이고 있었다(POST 를 세어서 확인했다).
     `tests/_nosheet.js` 머리말이 처음부터 이르던 일이다. */
  await noSheet(browser);
  const p = await browser.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 30000 });

  /* 진단서(책)는 PDF 를 뽑을 때만 조판된다. 여기서는 그 함수를 그대로 불러
     HTML 만 받아 본다 — 화면에 붙이지 않으므로 다른 검사에 영향이 없다. */
  const r = await p.evaluate(async () => {
    const eid = 'hwol-2018';
    const ex = FINAL_EXAMS.find(e => e.id === eid);
    openExam(eid);
    // 3의 배수는 찍고 틀리게, 5의 배수는 비우고, 나머지는 맞게
    let correct = 0, W = 0; const wrong = [];
    for (let q = 1; q <= ex.nQ; q++) {
      const k = ex.key[q - 1];
      setAns(q, q % 5 === 0 ? 0 : (q % 3 === 0 ? ((k % 4) + 1) : k));
    }
    document.getElementById('nm').value = '분류점검';
    document.getElementById('sch').value = 'X중';
    scoreAuto();
    await new Promise(r => setTimeout(r, 700));
    for (let q = 1; q <= ex.nQ; q++) {
      const a = sel[q] || 0;
      if (okq(ex, q, a)) correct++; else { W++; wrong.push({ q: q, a: a }); }
    }
    const cs = cohortStats(ex);
    const html = buildBook(ex, sel, cs, correct, ex.nQ, W, wrong, {}, {});
    const d = document.createElement('div'); d.innerHTML = html;
    // 유형 띠를 나온 순서대로 (이름, 그 유형의 정답률)
    const bands = [].map.call(d.querySelectorAll('.bk-tyband'), b => {
      const n = b.querySelector('.bk-tyband-n').textContent;
      const m = /이 유형 (\d+)\/(\d+) 맞음/.exec(b.querySelector('.bk-tyband-s').textContent);
      return { n: n, r: m ? (+m[1]) / (+m[2]) : 0 };
    });
    // 문항 1개짜리 영역이 있는가 · 그 줄이 무엇을 말하는가
    const rows = [].map.call(d.querySelectorAll('.bk-areatbl tbody tr'), tr => {
      const td = tr.querySelectorAll('td');
      return { name: td[0].querySelector('.anm') ? '' : td[0].childNodes[0].textContent.trim(),
               co: td[3].textContent.trim(), tag: td[4].textContent.trim(),
               qs: td[0].querySelectorAll('.bk-qch').length,
               tys: !!td[0].querySelector('.bk-tys') };
    });
    /* '정복 현황' 도 같은 규칙을 지켜야 한다. 여태 여기만 문항 수 바닥이
       없어서, 문항 하나짜리 영역을 찍어 맞히면 100% → '정복' 이 됐다.
       한 번 본 것을 정복했다고 말해 주는 것은 칭찬이 아니라 가벼운 거짓말이고,
       진짜로 잡은 영역까지 같이 값이 떨어진다.
       (`docs/성적표를-읽는-사람.md` 4절) */
    const mot = document.createElement('div');
    mot.innerHTML = motivationSec(ex, sel || {});
    const mtxt = (mot.innerText || mot.textContent || '');
    const mm = /(\d+)개 영역 중\s*(\d+)개 정복/.exec(mtxt);
    const nQ = {};                  // 대분류마다 문항이 몇 개인가
    for (let q = 1; q <= ex.nQ; q++) {
      const a = ex.area[q - 1] || '';
      const bd = (typeof RX !== 'undefined' && RX[a]) ? a
        : ((typeof RXMAP !== 'undefined' && RXMAP[a]) || a);
      nQ[bd] = (nQ[bd] || 0) + 1;
    }
    return { rule: /판정 기준/.test(d.textContent),
             ruleWords: /문항이 2개 이상/.test(d.textContent) && /80% 이상이면 강점/.test(d.textContent),
             rows: rows, bands: bands,
             conqTotal: mm ? +mm[1] : null,
             conqNames: [].map.call(mot.querySelectorAll('.pill'), e => e.textContent.trim()),
             oneQ: Object.keys(nQ).filter(k => nQ[k] < 2),
             judgeable: Object.keys(nQ).filter(k => nQ[k] >= 2).length,
             apx: /유형으로 묶어 취약한 유형부터/.test(d.textContent) };
  });

  console.log(`\n■ 영역 ${r.rows.length}줄 · 유형 띠 ${r.bands.length}개`);
  chk('판정 기준이 성적표에 적혀 있다', r.rule, true);
  chk('기준이 숫자까지 적혀 있다', r.ruleWords, true);

  const one = r.rows.filter(x => /^1\/1$/.test(x.co));
  console.log(`  (문항 1개인 영역 ${one.length}개)`);
  chk('문항 1개인 영역은 빈칸이 아니다', one.every(x => x.tag.indexOf('판정 안 함') >= 0), true);
  chk('문항 2개 이상은 그 말을 안 쓴다',
    r.rows.filter(x => !/^\d+\/1$/.test(x.co)).every(x => x.tag.indexOf('판정 안 함') < 0), true);
  chk('영역마다 문항 번호가 보인다', r.rows.every(x => x.qs > 0), true);
  chk('영역마다 유형이 보인다', r.rows.every(x => x.tys), true);
  chk('문항 번호 개수가 정오의 분모와 같다',
    r.rows.every(x => x.qs === Number(x.co.split('/')[1])), true);

  console.log('  유형 순서: ' + r.bands.slice(0, 5).map(b => `${b.n}(${Math.round(b.r * 100)}%)`).join(' → '));
  chk('오답 노트가 유형으로 묶인다', r.bands.length > 1, true);
  chk('취약한 유형이 앞에 온다',
    r.bands.every((b, i) => i === 0 || r.bands[i - 1].r <= b.r + 1e-9), true);
  chk('머리글이 그 순서를 말한다', r.apx, true);

  /* 정복 현황도 '문항 2개 이상' 규칙을 지키는가.
     여태 여기만 바닥이 없어서 한 문항짜리 영역이 '정복' 으로 올라왔다. */
  console.log(`  정복: ${r.conqNames.join(' · ') || '(없음)'}`
              + ` · 분모 ${r.conqTotal} · 문항 1개인 영역 ${r.oneQ.length}개`);
  chk('정복 분모가 판정 가능한 영역 수와 같다', r.conqTotal, r.judgeable);
  chk('문항 1개인 영역은 정복으로 안 센다',
    r.conqNames.every(n => r.oneQ.indexOf(n) < 0), true);

  console.log('\n' + (errs.length ? 'JS 오류: ' + errs.slice(0, 3).join(' | ') : 'JS 오류 없음'));
  if (errs.length) fail++;
  await browser.close();
  console.log(fail ? `\n실패 ${fail}` : '\n전부 통과');
  process.exit(fail ? 1 : 0);
})();
