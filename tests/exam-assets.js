/* ============================================================
   회차 자료(문제지·해설) 링크 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   문제지 PDF 와 해설 파일은 회차마다 저장소에 같이 올라가는데, 앱에서 내려받을
   길이 없었다. 성적표 아래에 해설 링크가 하나 있었을 뿐이라 **채점을 해야만**
   닿을 수 있었다. 시험지를 나눠 주려고 여는 자리에는 아무것도 없었다.

   그리고 이름이 사실과 달랐다. 링크는 전부 '정답·개념 해설' 이었는데, 담긴
   내용은 회차마다 다르다 — 기출동형과 일부 KMChC 2024~2026 회차는
   문항별 풀이가 아직 없고 정답·영역·개념표까지다. 해설을 기대하고 연 사람이
   표만 보게 된다.

   여기서 지키는 것:
   - 모든 회차에 문제지·해설 파일이 실제로 있다(링크가 404 나면 안 된다)
   - solFull 이 해설 데이터와 어긋나지 않는다
   - 문항별 풀이가 없는 회차는 링크 이름이 '정답 · 개념표' 다
   - 답안 입력 화면에서 내려받을 수 있다(download 속성)

   실행:  node tests/exam-assets.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const EXAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));

console.log('── 링크가 가리키는 파일이 실제로 있다 ──');
{
  const noPdf = EXAMS.filter(e => !e.pdf || !fs.existsSync(path.join(ROOT, e.pdf))).map(e => e.id);
  chk('문제지 PDF 가 전 회차에 있다', noPdf, []);
  const missingExtra = EXAMS.flatMap(e => ['answerPdf', 'bookPdf']
    .filter(k => e[k] && !fs.existsSync(path.join(ROOT, e[k])))
    .map(k => `${e.id}:${k}`));
  chk('등록한 공식 정답·완성본 PDF 가 있다', missingExtra, []);
  const noSol = EXAMS.filter(e => !fs.existsSync(path.join(ROOT, `sol-final-${e.id}.html`))).map(e => e.id);
  chk('해설 파일이 전 회차에 있다', noSol, []);
  // 빈 껍데기를 링크하면 받는 쪽에서야 알게 된다
  const tiny = EXAMS.filter(e => fs.statSync(path.join(ROOT, `sol-final-${e.id}.html`)).size < 2048).map(e => e.id);
  chk('해설 파일이 껍데기가 아니다', tiny, []);
}

console.log('\n── 이름이 내용과 맞는다 ──');
{
  // solFull 은 answers/<id>.json 에서 파생된다. 손으로 켜 두면 없는 해설을 있다고 한다.
  const drift = [];
  EXAMS.forEach(e => {
    const p = path.join(ROOT, 'answers', `${e.id}.json`);
    let has = false;
    if (fs.existsSync(p)) {
      const q = JSON.parse(fs.readFileSync(p, 'utf8')).questions || {};
      has = Object.keys(q).some(k => String(q[k].explanation || '').trim()
                                  || String(q[k].explanationHtml || '').trim());
    }
    if (!!e.solFull !== has) drift.push(`${e.id}: solFull=${!!e.solFull} · 실제 해설=${has}`);
  });
  chk('solFull 이 해설 데이터와 같다', drift, []);
  chk('문항별 해설이 있는 회차 수', EXAMS.filter(e => e.solFull).length, 29);
  // 산과염기 60제에 풀이를 써 넣었다. 데이터에서 파생되므로 값이 저절로 따라온다.
  chk('산과염기 60제에 풀이가 생겼다',
      EXAMS.find(e => e.id === 'sanyeom-60').solFull, true);
}

console.log('\n── 앱이 그 이름과 다운로드를 붙인다 ──');
{
  const ctx = { esc: s => String(s) };
  vm.createContext(ctx);
  const cut = name => {
    const at = SRC.search(new RegExp(`^function ${name}\\(`, 'm'));
    if (at < 0) throw new Error(`final.html 에서 ${name} 을 못 찾았다`);
    let depth = 0, end = -1;
    for (let j = SRC.indexOf('{', at); j < SRC.length; j++) {
      if (SRC[j] === '{') depth++;
      else if (SRC[j] === '}') { depth--; if (!depth) { end = j + 1; break; } }
    }
    return SRC.slice(at, end);
  };
  vm.runInContext([cut('examSolLabel'), cut('examAssetsHTML')].join('\n'), ctx);

  const thin = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'donghyung-1'));
  const full = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'jmchc-6'));
  const latest = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'kmchc-2026-1-simhwa'));
  chk('풀이 없는 회차는 개념표라고 적는다', /정답 · 개념표/.test(thin), true);
  chk('풀이 없는 회차를 해설이라 하지 않는다', /문항별 해설/.test(thin), false);
  chk('풀이 있는 회차는 문항별 해설이라 적는다', /정답 · 문항별 해설/.test(full), true);

  chk('문제지가 걸린다', /href="donghyung-1-problem\.pdf" download/.test(thin), true);
  chk('새 회차 공식 정답을 직접 받는다',
      /href="kmchc-2026-1-simhwa-answer\.pdf" download/.test(latest), true);
  chk('새 회차 문제편·해설편을 직접 받는다',
      /href="kmchc-2026-1-simhwa-solution-book\.pdf" download/.test(latest), true);
  chk('해설이 내려받아진다', /href="sol-final-donghyung-1\.html" download/.test(thin), true);
  chk('브라우저로 열어 볼 수도 있다', /target="_blank"/.test(thin), true);
  chk('새 창 링크에 rel=noopener 가 있다', /rel="noopener"/.test(thin), true);

  // 답안 입력 화면에 실제로 꽂혀 있는지 — 함수만 있고 안 부르면 화면엔 없다
  chk('답안 입력 화면이 이 줄을 그린다', /\$\{examAssetsHTML\(cur\)\}/.test(SRC), true);
  chk('성적표 링크도 같은 이름을 쓴다', /\$\{examSolLabel\(cur\)\}/.test(SRC), true);
  // 인쇄물에는 넣지 않는다(종이에 찍힌 링크는 누를 수 없다)
  chk('인쇄할 때는 숨긴다', /@media print\{\.assets\{display:none\}\}/.test(SRC), true);
}

console.log('\n── 해설지가 데이터를 그대로 담는다 ──');
{
  /* 해설을 데이터에 써 넣어도 해설지 파일이 옛날 그대로면, 선생님이 내려받은
     파일에는 아무것도 안 늘어난다. 생성기가 만든 페이지만 여기서 검사한다. */
  const page = fs.readFileSync(path.join(ROOT, 'sol-final-sanyeom-60.html'), 'utf8');
  const q = JSON.parse(fs.readFileSync(path.join(ROOT, 'answers', 'sanyeom-60.json'), 'utf8')).questions;
  const withExp = Object.keys(q).filter(k => String(q[k].explanation || '').trim());
  chk('60문항에 해설이 있다', withExp.length, 60);
  chk('해설지에 사고과정이 실렸다', (page.match(/사고과정/g) || []).length >= 60, true);
  chk('문항 블록이 60개다', (page.match(/문제 \d+<\/span>/g) || []).length, 60);

  /* 문제 지문은 싣지 않는다 — 문제지가 따로 있고, 해설지에 옮겨 적으면
     같은 것을 한 번 더 퍼뜨리는 셈이다. */
  chk('문제 지문을 옮겨 적지 않았다', /class="stem"/.test(page), false);

  /* 검수 전 해설을 검수된 것처럼 내보내면 읽는 쪽이 구분할 수 없다.
     지금은 전 문항이 검수를 마쳤으므로 안내가 없어야 한다 — 다만 규칙 자체는
     살아 있어야 한다. '검수 전 문항이 있을 때만 안내가 뜬다'로 검사한다. */
  const unreviewed = Object.keys(q).filter(k => !String(q[k].verificationStatus || '').startsWith('verified'));
  chk('전 문항이 검수를 마쳤다', unreviewed, []);
  chk('검수 전 안내가 뜨는지는 데이터가 정한다',
      /검수 전 해설입니다/.test(page), unreviewed.length > 0);
  chk('생성기에 안내 규칙이 살아 있다',
      /검수 전 해설입니다/.test(fs.readFileSync(path.join(ROOT, 'tools', 'gen_sol_page.py'), 'utf8')), true);

  /* 해설은 정답 키에 맞춰 쓴다. 답을 되묻는 메모가 남아 있으면
     학생·학부모가 보는 해설지에 '확인 필요'가 찍힌다. */
  chk('되묻는 메모가 남아 있지 않다',
      Object.keys(q).filter(k => q[k].reviewNote), []);
  chk('해설지에 확인 필요 표시가 없다', /확인 필요/.test(page), false);

  // 해설이 실제로 정답 키를 가리키는지 — 화살표 뒤 기호가 정답과 같아야 한다
  const CIRC = { 1: '①', 2: '②', 3: '③', 4: '④' };
  const mismatch = Object.keys(q).filter(k => {
    const m = String(q[k].explanation || '').match(/→ ([①②③④])/);
    return !m || m[1] !== CIRC[Number(q[k].answer)];
  });
  chk('60문항 해설이 모두 정답 키를 가리킨다', mismatch, []);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
