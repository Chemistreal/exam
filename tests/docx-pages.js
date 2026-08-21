/* ============================================================
   성적표 Word — 장이 밀리지 않는다 (실제로 찍어서 잰다)

   선생님이 만든 파일을 보내 주셨다(2026-08-17). 표지 다음 2쪽이
   **채점일 한 줄만 있는 빈 장**이었다.

   까닭은 표지 아래 여백이 **5200 트윕으로 박혀** 있었기 때문이다. 그 값은
   표지 아래 두 줄(숫자 셋 · 채점일)이 생기기 전에 맞춰 놓은 것이라, 줄이
   늘 때마다 표지가 바닥으로 밀렸다. 찍어서 재어 보니 마지막 줄 아래 여유가
   **30.7pt — 딱 한 줄**이었다. 워드는 글꼴 높이를 이 renderer 와 다르게
   재므로 그 한 줄을 못 버틴다. 이쪽에서는 멀쩡해 보이고 워드에서만 깨진다.

   목차도 같은 병이었다. 칸 여백이 160 트윕으로 박혀 있어 **열 줄까지만**
   들어갔고, 열세 줄이 되자 세 줄이 다음 장으로 넘어갔다.

   그래서 «눈으로 보기» 가 아니라 **찍어서 잰다**:
     · docx 를 만들고
     · LibreOffice 로 PDF 로 찍고
     · 표지 마지막 글자가 바닥에서 몇 pt 떨어져 있는지 재고
     · 거의 빈 장이 있는지 센다

   ⚠ 이 자는 LibreOffice(writer)와 poppler 가 있어야 돈다. 없으면 조용히
     지나가지 않는다 — REQUIRE_SOFFICE 가 켜져 있으면 **멈춘다**.
     건너뛴 것은 초록으로 세지 않는다.

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/docx-pages.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(600);
const fs = require('fs'), path = require('path'), os = require('os');
const { execFileSync } = require('child_process');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);

function have(cmd, args) {
  try { execFileSync(cmd, args, { stdio: 'ignore', timeout: 120000 }); return true; }
  catch (e) { return false; }
}
/* soffice 는 --version 이 되면서도 writer 모듈이 없으면 **어떤 파일도 못 연다**.
   실제로 이 환경이 그랬다(core 만 깔려 있었다). 있는 척 넘어가면 안 되므로
   여기서 그 표를 직접 본다. */
function sofficeCanWrite() {
  const reg = ['/usr/lib/libreoffice/share/registry/writer.xcd',
               '/usr/lib64/libreoffice/share/registry/writer.xcd'];
  return have('soffice', ['--version']) && reg.some(p => fs.existsSync(p));
}

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) { console.log('실패: playwright 를 찾지 못했다'); process.exit(1); }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}
const noSheet = require('./_nosheet.js');
const seal = require('./_seal.js');

const OUT = path.join(os.tmpdir(), 'chemistreal-docx-pages');
let fail = 0;
const chk = (n, ok, info) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (ok ? '' : '   ' + info));
  if (!ok) fail++;
};

(async () => {
  if (!sofficeCanWrite() || !have('pdftotext', ['-v'])) {
    const msg = 'LibreOffice(writer) 또는 poppler(pdftotext) 가 없다 — 장을 찍어 볼 수 없다';
    if (process.env.REQUIRE_SOFFICE) { console.log('실패: ' + msg); process.exit(1); }
    console.log('건너뜀: ' + msg); process.exit(0);
  }
  fs.mkdirSync(OUT, { recursive: true });

  const b = seal(await chromium.launch({ executablePath: CHROMIUM, args: ['--no-sandbox'] }));
  await noSheet(b);
  const ctx = await b.newContext({ acceptDownloads: true });
  const p = await ctx.newPage();
  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(700);

  /* 선생님 화면과 같은 조건으로 만든다 — **채점일이 있는** 경우가 가장 길다.
     짧은 쪽만 재면 넘치는 경우를 영영 못 본다. */
  const built = await p.evaluate(async () => {
    localStorage.clear();
    window.__gradedOn = '2026-08-17';
    const ex = FINAL_EXAMS.find(x => x.id === 'hwol-2024') || FINAL_EXAMS[0];
    openExam(ex.id);
    document.getElementById('nm').value = '박바다';
    document.getElementById('sch').value = '대원국제중';
    const ge = document.getElementById('grd'); if (ge) ge.value = '3';
    for (let q = 1; q <= cur.nQ; q++) {
      const acc = (cur.multi && cur.multi[q]) || [cur.key[q - 1]];
      const g = acc[0] || 1;
      setAns(q, (q % 12 < 5) ? ((g % 4) + 1) : g);
    }
    scoreAuto();
    await new Promise(r => setTimeout(r, 2500));
    return { title: cur.title, nQ: cur.nQ };
  });
  await p.waitForTimeout(800);
  const [dl] = await Promise.all([
    p.waitForEvent('download', { timeout: 300000 }),
    p.evaluate(() => downloadReportDOCX()),
  ]);
  const docx = path.join(OUT, 'r.docx');
  await dl.saveAs(docx);
  await b.close();
  console.log('만든 성적표: ' + built.title + ' · ' + built.nQ + '문항 · '
    + Math.round(fs.statSync(docx).size / 1024) + 'KB');

  /* ── 찍는다 ── */
  const pdf = path.join(OUT, 'r.pdf');
  fs.rmSync(pdf, { force: true });
  execFileSync('soffice', ['-env:UserInstallation=file://' + path.join(OUT, 'prof'),
    '--headless', '--norestore', '--convert-to', 'pdf', '--outdir', OUT, docx],
    { stdio: 'ignore', timeout: 900000 });
  chk('워드 파일이 실제로 열린다', fs.existsSync(pdf), 'PDF 가 안 만들어졌다');
  if (!fs.existsSync(pdf)) process.exit(1);

  /* ── ① 표지가 한 장 안에서 끝나고, 바닥까지 여유가 있다 ── */
  const bboxPath = path.join(OUT, 'p1.xml');
  execFileSync('pdftotext', ['-bbox-layout', '-f', '1', '-l', '1', pdf, bboxPath], { timeout: 120000 });
  const x1 = fs.readFileSync(bboxPath, 'utf8');
  const H = parseFloat((x1.match(/height="([\d.]+)"/) || [])[1] || '842');
  const yMaxes = [...x1.matchAll(/yMax="([\d.]+)">/g)].map(m => parseFloat(m[1]));
  const bottomInk = Math.max.apply(null, yMaxes);
  const BOTTOM_MARGIN = 60;                       // 1200 트윕
  const slack = H - BOTTOM_MARGIN - bottomInk;
  console.log('  표지 마지막 글자 ' + bottomInk.toFixed(1) + 'pt · 본문 바닥 '
    + (H - BOTTOM_MARGIN).toFixed(1) + 'pt · 남은 여유 ' + slack.toFixed(1) + 'pt');
  /* 80pt ≈ 두 줄. 워드가 글꼴을 이보다 더 크게 재는 일은 없다.
     여기가 30.7pt 였을 때 워드에서 한 줄이 넘어갔다. */
  chk('표지 아래에 두 줄치 여유가 남는다 (≥80pt)', slack >= 80, '여유 ' + slack.toFixed(1) + 'pt');

  /* ── ② 거의 빈 장이 없다 ── */
  const txt = execFileSync('pdftotext', ['-layout', pdf, '-'], { encoding: 'utf8', maxBuffer: 1 << 28 });
  /* ⚠ split('\f') 의 **마지막 조각은 장이 아니다**(끝 개행 뒤 빈 문자열).
     처음에 이걸 장으로 세어 «마지막에 빈 장이 있다» 고 잘못 읽었다. */
  const pages = txt.split('\f');
  if (pages.length && pages[pages.length - 1].trim() === '') pages.pop();
  const inkOf = s => s.split('\n').map(l => l.trim())
    .filter(l => l && !/CHEMISTREAL/.test(l) && !/^\d+\s*\/\s*\d+$/.test(l))
    .join('').length;
  const ink = pages.map((s, i) => ({ n: i + 1, ink: inkOf(s) }));

  /* 무엇을 막고 무엇을 적어만 둘지 — 이 둘은 다르다.

     **막는 것**: 글자가 거의 없는 장. 선생님이 받은 파일의 2쪽이 그랬다
       (채점일 한 줄, 30자 남짓). 그런 장은 박아 둔 여백 탓이고, 고치면 사라진다.

     **적어만 두는 것**: 한 절의 끝 두세 줄이 넘어간 장. 이건 글 길이 탓이라
       학생마다 다르다 — 처방이 세 영역인 학생과 여섯 영역인 학생이 다르고,
       renderer 가 바뀌어도 달라진다(여기 94쪽 · 이 자리 96쪽). 고정된 값으로
       막으려 하면 **엉뚱한 빨간불**이 되고, 그러면 아무도 이 자를 안 본다.
       세어서 남기고, 줄일지는 사람이 정한다. */
  const BLANKISH = 40;      // 한글 한 줄이 대략 40자
  const THINNISH = 200;
  /* 표지는 원래 글자가 적은 장이다 — 끝자락 목록에 넣으면 늘 한 줄이 뜨고,
     늘 뜨는 줄은 곧 안 읽는 줄이 된다. 다만 «거의 빈 장» 에서는 안 뺀다 —
     선생님이 받은 파일에서 문제가 난 곳이 바로 표지 다음이었다. */
  const blank = ink.filter(x => x.ink < BLANKISH);
  const thin = ink.filter(x => x.n > 1 && x.ink >= BLANKISH && x.ink < THINNISH);
  console.log('  전체 ' + pages.length + '쪽 · 거의 빈 장 ' + blank.length
    + '개 · 끝자락만 남은 장 ' + thin.length + '개'
    + (thin.length ? ' (' + thin.map(x => x.n + '쪽 ' + x.ink + '자').join(', ') + ')' : ''));
  chk('거의 빈 장이 없다', blank.length === 0,
    blank.map(x => x.n + '쪽(글자 ' + x.ink + ')').join(', '));

  /* ── ③ 목차가 한 장에 다 들어간다 ── */
  const tocPages = pages.map((s, i) => ({ n: i + 1, s }))
    .filter(x => /CONTENTS|목차/.test(x.s));
  chk('목차가 있다', tocPages.length > 0, '목차를 못 찾았다');
  if (tocPages.length) {
    const first = tocPages[0].n;
    /* 목차 다음 장에 목차 항목이 이어지면 두 장으로 갈린 것이다. 항목은
       «두 자리 번호 한 줄» 로 나오므로 그것을 센다. */
    const next = pages[first] || '';
    const spill = (next.match(/^\s*\d{2}\s*$/gm) || []).length
                + (next.match(/부록\s*[ⅠⅡⅢ]/g) || []).length;
    chk('목차가 다음 장으로 안 넘어간다', spill === 0, (first + 1) + '쪽에 목차 항목 ' + spill + '개');
  }

  /* ── ④ 표지에 있어야 할 것이 다 있다(줄여서 지워지지 않았다) ── */
  const cover = pages[0] || '';
  for (const must of ['성적 진단서', '박바다', built.title.replace(/\s+/g, ' ').split(' ')[0], '발행일']) {
    chk('표지에 「' + must + '」 가 있다', cover.replace(/\s+/g, '').includes(must.replace(/\s+/g, '')),
      cover.slice(0, 120).replace(/\n/g, ' '));
  }

  console.log(fail ? ('\n실패 ' + fail + '건') : '\n장이 밀리지 않는다.');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
