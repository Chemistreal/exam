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
  /* 문제지가 **정말로 없는** 회차가 있다. j0(조준모의고사 0회)이 그렇다 —
     문항 본문도 문제지 PDF 도 저장소에 없고, 남은 것은 정답·영역·개념과
     오개념 한 줄뿐이다.

     그런 회차를 이 검사가 막으면 두 가지 중 하나가 된다: 회차를 아예 안
     들이거나(학부모가 옛 양식 성적표를 받는다), 없는 파일을 가리키는 링크를
     걸거나(눌러서 404 를 만난다). 둘 다 나쁘다.

     그래서 **말하게 한다.** `noPdf` 에 까닭을 적은 회차만 통과시킨다. 빈
     문자열이나 생략은 안 된다 — 조용히 빠지는 길을 남기면 다음 회차가 그리로
     샌다. 화면 쪽(examMaterialsHTML)은 이미 `if(exam.pdf)` 로 감싸 두어서
     pdf 가 없으면 링크를 아예 안 만든다. */
  const noPdf = EXAMS.filter(e => !e.pdf && !(typeof e.noPdf === 'string' && e.noPdf.trim()))
                     .map(e => e.id);
  chk('문제지 PDF 가 없으면 까닭이 적혀 있다', noPdf, []);
  const brokenPdf = EXAMS.filter(e => e.pdf && !fs.existsSync(path.join(ROOT, e.pdf))).map(e => e.id);
  chk('등록한 문제지 PDF 가 실제로 있다', brokenPdf, []);
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
  /* 해설은 회차마다 손으로 써 넣는 중이라 이 수는 **늘기만 한다**. 정확한
     값으로 박아 두면 한 회차를 채울 때마다 이 검사가 깨져, 고치는 사람이
     기대값을 기계적으로 올리게 된다 — 그러면 줄어드는 것도 못 잡는다.
     바닥만 지킨다. 어긋남 자체는 바로 위 'solFull 이 해설 데이터와 같다'
     가 본다. 회차를 채울 때 이 바닥도 함께 올려라.

     ⚠ 내려도 되는 때는 회차를 **일부러** 뺐을 때뿐이고, 그때는 왜 뺐는지
        여기 적는다. 아무 때나 내릴 수 있으면 바닥은 바닥이 아니다.
        38 → 35 : KMChC 일반과정 세 회차(2025-1 · 2025-2 · 2026-1)를 뺐다.
        같은 회차의 심화과정만 보기로 해서다 (2026-08-08).
        35 → 36 : 그 셋 중 2025-1 일반을 되살렸다. 선생님이 그 회차 교재를
        새로 만들어 다시 보기로 하셨다 (2026-08-18).
        36 → 38 : 남은 일반 두 회차(2025-2 · 2026-1)도 되살렸다. 뺐던 셋이
        이로써 다 돌아왔다 (2026-08-18). */
  const FULL_FLOOR = 38;
  const full = EXAMS.filter(e => e.solFull).length;
  chk(`문항별 해설이 있는 회차 수(바닥 ${FULL_FLOOR})`, full >= FULL_FLOOR, true);
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

  /* '풀이 없는 회차' 본보기는 **골라서 박지 않는다**. 예전에는 donghyung-1
     이었는데 그 회차에 해설을 써 넣자 이 검사가 깨졌다 — 좋은 일이 검사를
     깨뜨리면 안 된다. 지금 풀이가 없는 회차를 그때그때 집는다.

     그러다 2026-08-07 에 **전 회차에 해설이 들어가** 집을 회차가 없어졌다.
     검사를 지우면 나중에 해설 없는 회차가 새로 들어왔을 때 '정답 · 개념표'
     로 적히는지 아무도 안 본다. 그래서 규칙은 남기고, 집을 것이 없을 때는
     가짜 회차를 하나 지어 **이름 규칙만** 확인한다(파일 검사는 진짜로 한다). */
  const thinExam = EXAMS.find(e => !e.solFull)
    || Object.assign({}, EXAMS[0], { id: '__풀이없음__', solFull: false });
  /* ⚠ **자리가 바뀌었다**(2026-08-10). 이 검사는 여태 '답 넣는 화면에
     정답·해설 링크가 걸리는가' 를 지키고 있었다. 그런데 그 화면이 바로
     답안지 위다 — 선생님이 문제지 PDF 에 답이 실려 있다고 알려 주셔서
     열어 보다가, 화면 쪽에도 같은 구멍이 있는 것을 봤다.

     그래서 `examAssetsHTML(exam, graded)` 로 갈랐다. 검사도 같이 옮긴다 —
     **없애는 것이 아니라 자리를 옮기는 것**이므로, 채점 뒤에는 그대로
     있어야 한다는 것까지 여기서 지킨다. (답 넣기 전에 없다는 것은
     `tests/answer-not-before.js` 가 실제 브라우저에서 본다.) */
  /* 자료 칸을 거는 자의 몸통. 여기만 따로 보아야 «성적표 어딘가에 그 글자가
     있다» 가 아니라 «이 자가 그것을 건다» 를 재게 된다. */
  const MAT = (SRC.match(/function examMaterialsHTML[\s\S]*?\n}/) || [''])[0];
  const thin = ctx.examAssetsHTML(thinExam, true);
  const full = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'jmchc-6'), true);
  const latest = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'kmchc-2026-1-simhwa'), true);
  const before = ctx.examAssetsHTML(EXAMS.find(e => e.id === 'kmchc-2026-1-simhwa'), false);
  chk('풀이 없는 회차는 개념표라고 적는다', /정답 · 개념표/.test(thin), true);
  chk('풀이 없는 회차를 해설이라 하지 않는다', /문항별 해설/.test(thin), false);
  chk('풀이 있는 회차는 문항별 해설이라 적는다', /정답 · 문항별 해설/.test(full), true);

  /* 파일이 실제로 걸리는지는 **진짜 회차**로 본다 — 가짜에는 파일이 없다. */
  const realExam = EXAMS.find(e => e.id === 'jmchc-6');
  chk('문제지가 걸린다',
      new RegExp(`href="${realExam.pdf}" download`).test(full), true);
  chk('채점 뒤 공식 정답을 직접 받는다',
      /href="kmchc-2026-1-simhwa-answer\.pdf" download/.test(latest), true);
  chk('채점 뒤 문제편·해설편을 직접 받는다',
      /href="kmchc-2026-1-simhwa-solution-book\.pdf" download/.test(latest), true);
  chk('채점 뒤 해설이 내려받아진다',
      new RegExp(`href="sol-final-${realExam.id}\\.html" download`).test(full), true);
  chk('브라우저로 열어 볼 수도 있다', /target="_blank"/.test(full), true);
  chk('새 창 링크에 rel=noopener 가 있다', /rel="noopener"/.test(full), true);

  // ── 답 넣기 전에는 문제지뿐이다 ────────────────────────────────
  chk('답 넣기 전에도 문제지는 걸린다', /kmchc-2026-1-simhwa-problem\.pdf/.test(before), true);
  chk('답 넣기 전에는 공식 정답이 없다', /answer\.pdf/.test(before), false);
  chk('답 넣기 전에는 문제편·해설편이 없다', /solution-book\.pdf/.test(before), false);
  chk('답 넣기 전에는 해설 링크가 없다', /sol-final-/.test(before), false);

  // 답안 입력 화면에 실제로 꽂혀 있는지 — 함수만 있고 안 부르면 화면엔 없다
  chk('답안 입력 화면이 이 줄을 그린다', /\$\{examAssetsHTML\(cur\)\}/.test(SRC), true);
  /* 성적표에도 정답·해설이 남아 있는지 — **옮긴 것이지 없앤 것이 아니다.**
     2026-08-13 에 자리가 한 번 더 옮겨졌다. 아래 단추 줄에 낱개로 걸려 있던
     것을 오답정리 바로 뒤 「시험지 · 해설 내려받기」 칸으로 모았다(선생님
     요청 — 문제지도 같이 준다). 같은 링크가 두 자리에 있으면 한쪽만 고쳤을
     때 갈리므로 단추 줄에서는 뺐다.

     여기서 지키려는 것은 «성적표에서 정답·해설이 사라지지 않았나» 이지
     «어느 줄에 적혀 있나» 가 아니다. 그래서 자리가 아니라 **거는 자를**
     본다. 실제로 화면에 그려지는지는 `tests/exam-materials.js` 가 진짜
     브라우저에서 본다 — 글자 찾기로는 «부르기만 하고 안 그리는» 것을
     못 잡는다. */
  chk('성적표가 자료 칸을 그린다', /\$\{examMaterialsHTML\(cur\)\}/.test(SRC), true);
  chk('그 칸이 공식 정답을 건다', /exam\.answerPdf\)/.test(MAT), true);
  chk('그 칸이 문제편·해설편을 건다', /exam\.bookPdf\)/.test(MAT), true);
  chk('그 칸이 문제지를 건다', /exam\.pdf\)/.test(MAT), true);
  chk('그 칸도 같은 이름을 쓴다', /examSolLabel\(exam\)/.test(MAT), true);
  chk('아래 단추 줄에는 같은 링크가 안 남았다',
      /class="pdf" href="sol-final-\$\{cur\.id\}/.test(SRC), false);
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
  /* 띠의 말은 학생어로 바꿨다(「해설 업데이트 안내」) — 「배포 전에 확인해
     주세요」 는 선생님께 하는 말이라 받는 학생을 헷갈리게 했다. */
  chk('검수 전 안내가 뜨는지는 데이터가 정한다',
      /해설 업데이트 안내/.test(page), unreviewed.length > 0);
  chk('생성기에 안내 규칙이 살아 있다',
      /해설 업데이트 안내/.test(fs.readFileSync(path.join(ROOT, 'tools', 'gen_sol_page.py'), 'utf8')), true);

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
