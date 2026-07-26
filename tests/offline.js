/* ============================================================
   오프라인 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   서비스워커가 `index.html` 에만 등록돼 있어서, 학생이 성적표 링크로 바로
   들어오면 등록이 아예 되지 않고 있었다. 즉 `final.html` 은 오프라인 지원이
   전혀 없었다. 학원에서 성적표를 열어 본 학생이 지하철에서 다시 열면 빈 화면이
   나온다.

   고친 뒤 지키는 것:
   - `final.html` 이 서비스워커의 제어를 받는다
   - 채점하면 자기가 틀린 문항의 크롭·해설·동형문제를 미리 받아 둔다
     (`loading="lazy"` 라 스크롤하지 않은 이미지는 저절로는 캐시되지 않는다)
   - 네트워크가 끊겨도 성적표와 오답노트가 그대로 열린다
   - 안 틀린 문항까지 미리 받지는 않는다(51MB 를 다 받아 두면 안 된다)

   [중요] Playwright 의 `setOffline` 은 이 환경에서 localhost 요청을 막지 못한다
   (직접 확인함 — 서비스워커를 지우고 한 번도 부른 적 없는 파일을 불러도 200이
   돌아온다). 그래서 **서버를 실제로 죽이고** 잰다. 그러지 않으면 오프라인
   테스트가 전부 통과하면서 아무것도 증명하지 못한다.

   실행:
       node tests/offline.js
   (playwright 와 크로미움 경로가 필요하다. 아래 상수를 환경에 맞게 고친다.)
   ============================================================ */
'use strict';
const { spawn } = require('child_process');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8932);
const ROOT = path.join(__dirname, '..');
const URL = `http://localhost:${PORT}/final.html`;

let fail = 0;
const chk = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + name +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};
const wait = ms => new Promise(r => setTimeout(r, ms));

/* 오답으로 만들 문항. 적게 잡아야 '미리 받은 것만 캐시됐는지'를 볼 수 있다. */
const WRONG = [1, 2, 3];
const EXAM = 'hwol-2018';

async function main() {
  let chromium;
  try { ({ chromium } = require(PLAYWRIGHT)); }
  catch (e) {
    console.log('건너뜀: playwright 를 찾지 못했다 (PLAYWRIGHT_MODULE 로 경로 지정)');
    return 0;
  }

  const server = spawn('python3', ['-m', 'http.server', String(PORT)],
    { cwd: ROOT, stdio: 'ignore' });
  const stop = () => { try { server.kill('SIGKILL'); } catch (e) {} };
  process.on('exit', stop);
  await wait(1200);

  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] });
  const page = await (await browser.newContext()).newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERR: ' + e.message));

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload({ waitUntil: 'networkidle' });   // 첫 방문은 controller 가 늦다
  chk('서비스워커가 final.html 을 제어',
    await page.evaluate(() => !!navigator.serviceWorker.controller), true);

  await page.evaluate(([examId, wrong]) => {
    openExam(examId);
    const nm = document.getElementById('nm'); if (nm) nm.value = '오프라인테스트';
    // 정답키가 0 인 전항정답 문항은 인정 답안 중 하나를 골라 무응답 오답을 막는다
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      setAns(q, acc[0] || 1);
    }
    wrong.forEach(q => setAns(q, (cur.key[q - 1] % 4) + 1));
    scoreAuto();
  }, [EXAM, WRONG]);

  const warmed = await page.evaluate(() => new Promise(res => {
    const t = setTimeout(() => res(null), 20000);
    navigator.serviceWorker.addEventListener('message', e => {
      if (e.data && e.data.type === 'warmed') { clearTimeout(t); res(e.data); }
    });
  }));
  chk('미리 받기 요청 = 해설1 + 동형2 + 크롭' + WRONG.length,
    warmed && warmed.asked, 3 + WRONG.length);

  // ── 여기서부터 진짜 오프라인 ──
  stop();
  await wait(900);
  chk('서버가 정말 죽었는지(캐시에 없는 파일은 실패해야)',
    await page.evaluate(async () => {
      try { await fetch('crops/hwol-2013/7.png', { cache: 'no-store' }); return '살아있음'; }
      catch (e) { return '죽음'; }
    }), '죽음');

  let loaded = true;
  try { await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 20000 }); }
  catch (e) { loaded = false; }
  chk('오프라인에서 final.html 열림', loaded, true);

  const got = await page.evaluate(async examId => {
    const ok = async u => { try { return (await fetch(u, { cache: 'no-store' })).ok; } catch (e) { return false; } };
    return {
      ans: await ok(`answers/${examId}.json`),
      dh1: await ok(`donghyung/${examId}.json`),
      dh2: await ok('donghyung/kmchc-2018.json'),
      crop: await ok(`crops/${examId}/1.png`),
      other: await ok(`crops/${examId}/59.png`),
    };
  }, EXAM);
  chk('오프라인 원문 해설', got.ans, true);
  chk('오프라인 동형문제 ①', got.dh1, true);
  chk('오프라인 동형문제 ②', got.dh2, true);
  chk('오프라인 틀린 문항 크롭', got.crop, true);
  chk('안 틀린 문항까지 받아 두지는 않음', got.other, false);

  const rendered = await page.evaluate(async ([examId, wrong]) => {
    openExam(examId);
    const nm = document.getElementById('nm'); if (nm) nm.value = '오프라인테스트';
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      setAns(q, acc[0] || 1);
    }
    wrong.forEach(q => setAns(q, (cur.key[q - 1] % 4) + 1));
    scoreAuto();
    await new Promise(r => setTimeout(r, 3000));
    // lazy 인 채로는 화면 밖 이미지가 안 뜨므로 강제로 즉시 로드시킨다
    document.querySelectorAll('.wb-card img.wb-qimage').forEach(i => { i.loading = 'eager'; });
    await new Promise(r => setTimeout(r, 1500));
    const cards = document.querySelectorAll('.wb-card');
    return {
      cards: cards.length,
      dh: [].slice.call(cards).map(c => c.querySelectorAll('.wb-dh').length),
      imgs: [].slice.call(document.querySelectorAll('.wb-card img.wb-qimage'))
        .filter(i => i.complete && i.naturalWidth > 0).length,
    };
  }, [EXAM, WRONG]);
  chk('오프라인에서 오답 카드', rendered.cards, WRONG.length);
  chk('오프라인에서 동형문제 2벌씩', rendered.dh, WRONG.map(() => 2));
  chk('오프라인에서 원문 이미지도 다 나옴', rendered.imgs, WRONG.length);
  chk('JS 오류 없음', errs, []);

  await browser.close();
  console.log(fail ? `\n결과: 실패 ${fail}건` : '\n결과: 전부 통과');
  return fail ? 1 : 0;
}

main().then(code => process.exit(code)).catch(e => {
  console.error('ERR', e.message);
  process.exit(1);
});
