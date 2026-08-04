#!/usr/bin/env node
/* ============================================================
   전체 검사 한 번에 — 그리고 **조용히 넘어가지 못하게**
   ------------------------------------------------------------
   브라우저가 필요한 검사는 playwright 가 없으면 스스로 건너뛰고 0 으로
   끝난다(CI 에는 브라우저가 없으니 그래야 한다). 그런데 손으로 스윕을
   돌릴 때도 똑같이 0 이 나와서, 건너뛴 것이 **통과한 것처럼** 보였다.

   실제로 그 때문에 석차 화면이 두 줄로 바뀐 뒤 rank-baseline 이 깨진 채로
   커밋 두 개를 지나갔다. 초록불이 거짓말을 하면 검사는 없느니만 못하다.

   여기서 하는 것:
   - tests/*.js 를 **스스로 찾아서** 돈다(목록을 손으로 맞추지 않는다)
   - 통과 · 건너뜀 · 실패를 따로 센다. 건너뛴 것은 초록으로 안 적는다
   - CI 목록(.github/workflows/tests.yml)에 없는 검사 파일을 짚어 준다
     — 만들어 놓고 CI 에 안 걸면 아무도 안 돌린다
   - python 검사는 CI 목록에서 그대로 읽어 온다(두 벌을 손으로 맞추지 않는다)

   실행:
       node tests/run.js                     # 브라우저 검사는 건너뛴다(경고)
       PLAYWRIGHT_MODULE=… CHROMIUM_PATH=… node tests/run.js    # 전부

   브라우저 검사까지 돌리려면 저장소 루트에서 정적 서버가 떠 있어야 한다:
       python3 -m http.server 8931
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const WF = path.join(ROOT, '.github', 'workflows', 'tests.yml');

const C = { ok: '\x1b[32m', skip: '\x1b[33m', bad: '\x1b[31m', dim: '\x1b[2m', off: '\x1b[0m' };
const pad = (s, n) => s + ' '.repeat(Math.max(0, n - [...s].length));

/* CI 가 실제로 무엇을 돌리는지 그대로 읽는다. 두 목록을 손으로 맞추면
   언젠가 어긋나고, 어긋난 쪽은 아무도 안 돌린다. */
function ciSteps() {
  if (!fs.existsSync(WF)) return [];
  return (fs.readFileSync(WF, 'utf8').match(/^\s*run:\s*(node|python3)\s+.+$/gm) || [])
    .map(l => l.replace(/^\s*run:\s*/, '').trim())
    .filter(c => !/pip install/.test(c));
}

const steps = ciSteps();
/* `_` 로 시작하는 것은 검사가 아니라 **다른 검사가 불러 쓰는 살림살이**다
   (`_gasenv.js` 는 앱스크립트 흉내, `_seal.js` 는 진짜 시트를 막는 마개).
   혼자서는 돌 수 없으니 CI 에 걸릴 수도 없는데, 여태 '안 걸린 파일' 로
   같이 세고 있었다. 진짜로 안 걸린 검사가 그 넷에 섞이면 안 보인다. */
const nodeFiles = fs.readdirSync(path.join(ROOT, 'tests'))
  .filter(f => f.endsWith('.js') && f !== 'run.js' && !f.startsWith('_')).sort();

/* CI 에 안 걸린 검사 파일 — 만들어 놓고 안 돌리면 없는 것과 같다. */
const orphan = nodeFiles.filter(f => !steps.some(c => c.includes('tests/' + f)));

let ok = 0, skipped = 0, failed = 0;
const skipNames = [], failNames = [];

function run(cmd) {
  const parts = cmd.split(/\s+/);
  /* 한 검사가 멈추면 스윕 전체가 멈춘다. 시간을 끊고 실패로 적는다 —
     '아직 도는 중' 과 '고장' 을 사람이 구분하려고 기다릴 이유가 없다. */
  const r = spawnSync(parts[0], parts.slice(1), { cwd: ROOT, encoding: 'utf8', timeout: 12*60*1000 });
  const out = (r.stdout || '') + (r.stderr || '') + (r.error ? '\n' + r.error.message : '');
  const skip = /^건너뜀:/m.test(out);
  const name = cmd.replace(/^(node|python3)\s+/, '');
  if (r.status !== 0) {
    failed++; failNames.push(name);
    console.log(`${C.bad}실패${C.off}  ${pad(name, 34)}`);
    out.split('\n').filter(l => /^\s*FAIL|Error|Traceback|기대/.test(l)).slice(0, 6)
      .forEach(l => console.log(`      ${C.dim}${l.trim()}${C.off}`));
  } else if (skip) {
    skipped++; skipNames.push(name);
    console.log(`${C.skip}건너뜀${C.off} ${pad(name, 33)} ${C.dim}브라우저 없음${C.off}`);
  } else {
    ok++;
    console.log(`${C.ok}통과${C.off}  ${pad(name, 34)}`);
  }
}

console.log(`검사 ${steps.length}개 · tests/*.js ${nodeFiles.length}개\n`);
steps.forEach(run);

if (orphan.length) {
  console.log(`\n${C.skip}CI 에 걸리지 않은 검사 파일${C.off} — 만들어 놓고 안 돌리면 없는 것과 같습니다`);
  orphan.forEach(f => console.log(`  tests/${f}`));
}

console.log(`\n통과 ${ok} · 건너뜀 ${skipped} · 실패 ${failed}`);
if (skipped) {
  /* 여기가 이 파일의 존재 이유다. 건너뛴 것을 초록으로 적으면, 브라우저에서만
     드러나는 고장이 커밋 여러 개를 지나간다 — 실제로 그랬다. */
  console.log(`${C.skip}\n주의: ${skipped}개가 브라우저가 없어 건너뛰었습니다. 통과한 것이 아닙니다.${C.off}`);
  console.log(`${C.dim}  전부 돌리려면: (저장소 루트에서 python3 -m http.server 8931 을 띄운 뒤)`);
  console.log(`  PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/run.js${C.off}`);
}
if (orphan.length) console.log(`${C.skip}CI 에 안 걸린 파일 ${orphan.length}개${C.off}`);

process.exit(failed || orphan.length ? 1 : 0);
