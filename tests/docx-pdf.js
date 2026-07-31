/* ============================================================
   성적표 PDF 는 Word 파일을 변환한 것이다 — 회귀 테스트
   ------------------------------------------------------------
   성적표를 두 벌 조판하면 반드시 어긋난다. 오늘 Word 쪽 표 한 줄을 고치고
   PDF 쪽을 안 고치면, 학생은 숫자가 다른 두 파일을 받는다. 어느 쪽이 맞는지
   받은 사람은 알 수 없다.

   그래서 PDF 는 형제가 아니라 사본이다. Packer 가 뱉은 그 .docx 바이트를
   그대로 펼쳐서 찍는다. 여기서 지키는 것:

   - 변환에 넘기는 바이트가 저장한 .docx 와 **같은 것**이다
   - 변환 쪽에서 성적표를 다시 만들지 않는다
   - Word 는 먼저 저장된다 — PDF 변환이 넘어져도 손에 남는 것이 있다
   - 두 파일 이름의 뿌리가 같다
   - 펼치는 데 필요한 파일이 실제로 저장소에 있다(없으면 변환이 죽는다)
   - 펼치는 라이브러리가 만드는 쪽의 전역 이름을 뺏은 채로 두지 않는다

   앞부분은 브라우저 없이 돈다(CI). 뒷부분은 playwright 가 있을 때만 돈다.

   실행 (뒷부분까지 보려면 먼저 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/docx-pdf.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};
function cut(name) {
  const at = SRC.search(new RegExp(`(?:async )?function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`final.html 에서 ${name} 을 못 찾았다`);
  let depth = 0, end = -1;
  for (let j = SRC.indexOf('{', at); j < SRC.length; j++) {
    if (SRC[j] === '{') depth++;
    else if (SRC[j] === '}') { depth--; if (!depth) { end = j + 1; break; } }
  }
  return SRC.slice(at, end);
}

console.log('── PDF 는 그 Word 파일에서 나온다 ──');
{
  const fn = cut('downloadReportDOCX');
  const made = /var blob\s*=\s*await Packer\.toBlob\(/.test(fn);
  chk('Word 를 먼저 만든다', made, true);
  // 변환에 넘기는 것이 방금 만든 그 blob 이어야 한다. 다른 이름이 오면
  // 어딘가에서 새로 만들었다는 뜻이다.
  chk('만든 blob 을 그대로 변환에 넘긴다', /docxBlobToPDFBlob\(blob\b/.test(fn), true);
  chk('저장도 그 blob 을 쓴다', /_saveBlob\(blob\s*,/.test(fn), true);

  // 순서: .docx 저장 → PDF 변환. 뒤집히면 변환에서 죽을 때 Word 도 못 받는다.
  const iDoc = fn.indexOf("_saveBlob(blob,"), iPdf = fn.indexOf('docxBlobToPDFBlob(');
  chk('Word 를 먼저 손에 쥐여 준다', iDoc >= 0 && iPdf > iDoc, true);
  chk('PDF 단계는 따로 감싼다(넘어져도 Word 는 남는다)',
      /try\{[\s\S]{0,400}docxBlobToPDFBlob\([\s\S]{0,400}\}catch\(/.test(fn), true);

  // 이름은 한 뿌리에서 갈라진다 — 학생 폴더에서 짝을 찾을 수 있어야 한다
  chk('두 파일 이름의 뿌리가 같다',
      /_saveBlob\(blob,base\+'\.docx'\)/.test(fn.replace(/\s/g, '')) &&
      /_saveBlob\(pdfBlob,base\+'\.pdf'\)/.test(fn.replace(/\s/g, '')), true);
}

console.log('\n── 변환 쪽이 성적표를 다시 만들지 않는다 ──');
{
  const fn = cut('docxBlobToPDFBlob');
  /* 조판 함수를 한 번이라도 부르면 그 순간 PDF 는 Word 의 사본이 아니게 된다. */
  ['buildBook', 'coverSec', 'tableSec', 'closingSecFinal', 'scoreAuto', 'renderReport'].forEach(n => {
    chk(`${n} 을 부르지 않는다`, new RegExp('\\b' + n + '\\s*\\(').test(fn), false);
  });
  chk('받은 블롭을 펼친다', /renderAsync\(blob\s*,/.test(fn), true);
  chk('쪽을 실제 쪽수대로 나눈다', /_repaginate\(/.test(fn), true);
  chk('종이에 붙박인 그림을 제자리에 앉힌다', /_anchorPageFloats\(/.test(fn), true);
  chk('쪽 번호를 채운다', /_pageNums\(/.test(fn), true);
  // 아흔 장을 매단 채로 아흔 번 찍으면 복제 비용이 제곱으로 는다
  chk('찍을 한 장만 붙여 둔다', /stage\.appendChild\(el\)/.test(fn), true);
  chk('펼치는 쪽이 넣은 스타일을 지우지 않는다', /host\.textContent=''/.test(fn), false);
}

console.log('\n── 펼치는 데 필요한 파일이 저장소에 있다 ──');
{
  ['vendor/docx-preview.min.js', 'vendor/jszip.min.js', 'vendor/jspdf.umd.min.js',
   'vendor/html2canvas.min.js', 'vendor/docx.iife.js'].forEach(f => {
    const p = path.join(ROOT, f);
    chk(f, fs.existsSync(p) && fs.statSync(p).size > 10000, true);
  });
  // 코드가 부르는 경로와 실제 파일 이름이 어긋나면 눌러 봐야 안다
  const asked = (SRC.match(/loadScriptOnce\('([^']+)'\)/g) || [])
    .map(s => s.replace(/^.*'(.*)'.*$/, '$1')).filter(s => /^vendor\//.test(s));
  chk('부르는 경로가 전부 실재한다',
      asked.filter(s => !fs.existsSync(path.join(ROOT, s))), []);
}

console.log('\n── 워터마크는 좌표로 적는다 ──');
{
  /* align:CENTER 는 읽는 쪽마다 해석이 갈린다. Word 결과는 같으므로
     좌표로 적어 두면 어디서 펼쳐도 가운데에 온다. */
  const fn = cut('markPara');
  chk('가로 위치가 좌표다', /horizontalPosition:\{relative:HPos\.PAGE,offset:/.test(fn), true);
  chk('align 을 쓰지 않는다', /HAlign\.CENTER/.test(fn), false);
}

/* ============================================================
   여기서부터는 브라우저가 있어야 한다.
   ============================================================ */
let chromium;
try { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')); }
catch (e) {
  console.log('\n(브라우저 검사 건너뜀: playwright 를 찾지 못했다)');
  console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
  process.exit(fail ? 1 : 0);
}

const PORT = Number(process.env.PORT || 8931);
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ acceptDownloads: true });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e)));

  const OUT = fs.mkdtempSync(require('os').tmpdir() + '/chemistreal-pdf-');
  const got = [];
  p.on('download', async d => {
    const f = path.join(OUT, got.length + path.extname(d.suggestedFilename() || '.bin'));
    await d.saveAs(f); got.push(f);
  });

  await p.goto(`http://localhost:${PORT}/final.html`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => typeof FINAL_EXAMS !== 'undefined' && FINAL_EXAMS.length, null, { timeout: 20000 });
  await p.evaluate(() => openExam(FINAL_EXAMS[0].id));
  await p.waitForTimeout(600);
  await p.evaluate(() => {
    document.getElementById('nm').value = '테스트학생';
    for (let q = 1; q <= cur.nQ; q++) setAns(q, (q % 5) || 1);
    scoreAuto();
  });
  await p.waitForTimeout(2500);

  /* 저장되는 이름과, 변환에 넘어가는 바이트를 함께 지켜본다. */
  await p.evaluate(() => {
    window.__log = { names: [], docxHash: null, pdfInHash: null };
    const sha = async blob => {
      const h = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
      return [...new Uint8Array(h)].map(x => x.toString(16).padStart(2, '0')).join('');
    };
    const realSave = window._saveBlob;
    window._saveBlob = function (blob, fn) {
      window.__log.names.push(fn);
      if (/\.docx$/.test(fn)) window.__log.pDocx = sha(blob).then(h => window.__log.docxHash = h);
      realSave(blob, fn);
    };
    const realPdf = window.docxBlobToPDFBlob;
    window.docxBlobToPDFBlob = function (blob, cb) {
      window.__log.pIn = sha(blob).then(h => window.__log.pdfInHash = h);
      return realPdf(blob, cb);
    };
  });

  console.log('\n── 눌러 보면 두 개가 떨어진다 ──');
  await p.evaluate(() => downloadReportDOCX());
  for (let i = 0; i < 300 && got.length < 2; i++) await p.waitForTimeout(1000);
  await p.evaluate(() => Promise.all([window.__log.pDocx, window.__log.pIn]));
  const log = await p.evaluate(() => window.__log);

  chk('파일이 둘 떨어진다', got.length, 2);
  chk('이름이 .docx 와 .pdf 다', log.names.map(n => n.replace(/^.*(\.\w+)$/, '$1')), ['.docx', '.pdf']);
  chk('이름의 뿌리가 같다',
      log.names[0].replace(/\.docx$/, '') === (log.names[1] || '').replace(/\.pdf$/, ''), true);
  chk('학생 이름이 파일명에 들어간다', /^테스트학생_/.test(log.names[0] || ''), true);

  console.log('\n── 변환한 것이 바로 그 Word 파일이다 ──');
  chk('저장한 .docx 와 변환에 넘긴 바이트가 같다', log.docxHash === log.pdfInHash && !!log.docxHash, true);

  console.log('\n── 떨어진 PDF 를 열어 본다 ──');
  const buf = fs.readFileSync(got[1]);
  chk('PDF 다', buf.slice(0, 5).toString(), '%PDF-');
  const pages = (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
  chk('여러 쪽이다', pages > 10, true);
  const mb = buf.toString('latin1').match(/\/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)/);
  chk('A4 다(210×297mm)', mb ? [Math.round(mb[1] * 25.4 / 72), Math.round(mb[2] * 25.4 / 72)] : null, [210, 297]);
  // .docx 도 진짜 Word 파일인지 — PK 서명과 워드 본문
  const dz = fs.readFileSync(got[0]);
  chk('.docx 도 온전하다', dz.slice(0, 2).toString() === 'PK' && dz.length > 100000, true);

  console.log('\n── 전역 이름을 돌려준다 ──');
  {
    /* docx-preview 도 window.docx 를 쓴다. 뺏은 채로 두면 다음 학생 성적표를
       만들 때 Packer 가 없다며 죽는다 — 한 명은 되고 두 번째부터 안 되는 종류의
       고장이라, 이름이 제자리로 왔는지 눈으로는 잡히지 않는다. */
    const r = await p.evaluate(async () => {
      await ensureDocxPreview();
      return { maker: !!(window.docx && window.docx.Packer), viewer: !!(window.__docxPreview && window.__docxPreview.renderAsync) };
    });
    chk('만드는 쪽 window.docx 가 살아 있다', r.maker, true);
    chk('펼치는 쪽도 따로 잡아 둔다', r.viewer, true);
    // 두 번째 학생도 저장된다 — 위가 무너지면 여기서 터진다
    const again = await p.evaluate(async () => {
      try { const Dx = await ensureDocxLib(); return !!(Dx && Dx.Packer && Dx.Document); }
      catch (e) { return String(e); }
    });
    chk('다음 학생 성적표도 만들 수 있다', again, true);
  }

  console.log('\n── 펼친 쪽이 Word 와 같은 자리에 놓인다 ──');
  /* .docx 안에서 배경은 '용지 왼쪽 위에서 얼마' 로 적혀 있다. 펼치는 쪽은
     그것을 글 흐름 위치에 놓아 버린다 — 배경이 여백만큼 밀린 채 찍히면
     프레임 한쪽이 종이 밖으로 나간다. 앉히는 규칙을 직접 세워 본다. */
  const place = await p.evaluate(() => {
    const sec = document.createElement('section');
    sec.style.cssText = 'position:relative;width:794px;height:1123px;padding:80px 72px;box-sizing:border-box';
    const h = document.createElement('header');
    const w1 = document.createElement('div');
    w1.style.cssText = 'display:block;position:relative;width:0px;height:0px;left:0pt;top:0pt';
    const im = document.createElement('div');
    im.style.cssText = 'width:794px;height:1123px'; w1.appendChild(im);
    const w2 = document.createElement('div');
    w2.style.cssText = 'display:block;position:relative;width:0px;height:0px;left:200.22pt;top:590.55pt';
    const im2 = document.createElement('div'); im2.style.cssText = 'width:260px;height:139px'; w2.appendChild(im2);
    h.appendChild(w1); h.appendChild(w2); sec.appendChild(h);
    document.body.appendChild(sec);
    _anchorPageFloats(sec);
    const r = sec.getBoundingClientRect();
    const a = im.getBoundingClientRect(), c = im2.getBoundingClientRect();
    const out = {
      frame: [Math.round(a.left - r.left), Math.round(a.top - r.top)],
      mark: [Math.round(c.left - r.left), Math.round(c.top - r.top)],
      z: w1.style.zIndex,
    };
    sec.remove(); return out;
  });
  chk('배경 프레임이 용지 왼쪽 위에 붙는다', place.frame, [0, 0]);
  chk('워터마크가 가로 가운데에 온다', place.mark[0], Math.round((794 - 260) / 2));
  chk('워터마크 높이도 문서가 적은 자리다', place.mark[1], Math.round(590.55 * 4 / 3));
  chk('배경은 글자 뒤로 간다', place.z, '0');

  console.log('\n── 꼬리말 쪽 번호를 채운다 ──');
  const nums = await p.evaluate(() => {
    const mk = () => {
      const sec = document.createElement('section');
      const f = document.createElement('footer');
      const pgh = document.createElement('p');
      const a = document.createElement('span'); a.textContent = 'CHEMISTREAL · 조준모 화학       ';
      const s = document.createElement('span'); s.textContent = '  /  ';
      pgh.appendChild(a); pgh.appendChild(s); f.appendChild(pgh); sec.appendChild(f);
      return sec;
    };
    const s1 = mk(); document.body.appendChild(s1); _pageNums(s1, 11, 91);
    const t1 = s1.querySelector('footer').textContent.replace(/\s+/g, ' ').trim(); s1.remove();
    // 꼬리말 모양이 바뀌면 손대지 않는다
    const s2 = document.createElement('section');
    s2.innerHTML = '<footer><p><span>다른 꼬리말</span></p></footer>';
    document.body.appendChild(s2); _pageNums(s2, 3, 9);
    const t2 = s2.querySelector('footer').textContent.trim(); s2.remove();
    return [t1, t2];
  });
  chk('몇 쪽 중 몇 쪽인지 적힌다', /11 \/ 91/.test(nums[0]), true);
  chk('모르는 꼬리말은 건드리지 않는다', nums[1], '다른 꼬리말');

  console.log('\n── 넘치는 쪽을 문단에서 나눈다 ──');
  const rp = await p.evaluate(() => {
    const host = document.createElement('div');
    const sec = document.createElement('section');
    sec.className = 'rptdocx';
    sec.style.cssText = 'position:relative;width:794px;box-sizing:border-box;padding:80px 72px;display:flex;flex-flow:column';
    const art = document.createElement('article');
    for (let i = 0; i < 40; i++) {
      const d = document.createElement('p');
      d.style.cssText = 'height:100px;margin:0'; d.textContent = 'P' + i; art.appendChild(d);
    }
    sec.appendChild(art); host.appendChild(sec); document.body.appendChild(host);
    _repaginate(host, 1123);
    const out = [].slice.call(host.querySelectorAll('section.rptdocx'))
      .map(s => [].slice.call(s.querySelectorAll('p')).map(x => x.textContent));
    host.remove();
    return { pages: out.length, first: out[0], all: out.flat().length };
  });
  chk('여러 쪽으로 나뉜다', rp.pages > 1, true);
  chk('한 쪽에 들어갈 만큼만 담는다', rp.first.length, 9);   // 1123-160 = 963 → 100px 짜리 9개
  chk('문단이 하나도 사라지지 않는다', rp.all, 40);
  chk('첫 쪽은 맨 앞부터', rp.first[0], 'P0');

  chk('콘솔에 예외가 없다', errs.filter(e => !/Failed to fetch|ERR_CONNECTION/.test(e)), []);
  fs.rmSync(OUT, { recursive: true, force: true });
  await b.close();
  console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
  process.exit(fail ? 1 : 0);
})();
