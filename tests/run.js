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

   ⚠ **두 판을 같이 돌리지 않는다.** 검사마다 제 서버를 띄우므로 겹치면
     뒤엣것이 빈 화면을 열고 "그게 화면에 없다" 고 말한다(tests/_serve.js).
     끝났는지 볼 때 `pgrep -f tests/run.js` 로 기다리면 **그 기다리는 명령
     자신이 잡혀** 영영 안 끝난다 — 실제로 그렇게 걸려서, 옛 판의 로그를
     이번 결과로 잘못 읽었다. 파일 이름을 매번 새로 주고 끝을 그 파일에서 본다.

     이 말은 여기 오래 적혀 있었는데 **막지는 않고 있었다.** 2026-08-14 에
     같은 실수를 두 번 했다 — 앞 판이 아직 도는 줄 모르고 새 판을 띄웠고,
     스물세 건이 빨간불이었다(전부 겹침 탓이었다). 적어 두는 것과 막는 것은
     다르다. 이제 **자물쇠를 건다**(아래 lock()): 이미 도는 판이 있으면 새
     판은 뜨자마자 멈추고 그렇게 말한다. `--force` 로 넘길 수는 있다 —
     기계가 죽어 자물쇠만 남은 경우가 있어서다.

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
/* 검사마다 **몇 초 걸렸는지** 적어 둔다. 다음 번에 빠른 것부터 돌리려고
   쓰고, `--fast` 가 무엇을 고를지도 여기서 정한다. 손으로 안 적는다. */
const DUR = path.join(__dirname, 'durations.json');

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

/* ── 자물쇠 ────────────────────────────────────────────────────────
   판 하나가 도는 동안 다른 판이 못 뜨게 한다. 겹치면 검사들이 서로의 서버를
   보고 «화면에 그게 없다» 고 말하는데, 그 빨간불은 **코드 탓이 아니라 겹침
   탓**이다. 한 번 겪으면 다음부터 빨간불을 안 믿게 된다.

   죽은 자물쇠는 스스로 치운다 — 그 번호의 프로세스가 살아 있는지 본다.
   (파일만 남기고 기계가 죽으면 영영 못 돌리게 되는 것이 더 나쁘다) */
const LOCK = path.join(require('os').tmpdir(), 'chemistreal-exam-tests.lock');
function lock() {
  if (process.argv.includes('--force')) return function () {};
  try {
    const old = Number(fs.readFileSync(LOCK, 'utf8'));
    let alive = false;
    try { process.kill(old, 0); alive = true; } catch (e) { alive = false; }
    if (alive) {
      console.log(`${C.bad}판이 이미 돌고 있다${C.off} (프로세스 ${old}).`);
      console.log('두 판이 겹치면 검사들이 서로의 서버를 보고 엉뚱한 빨간불을 낸다.');
      console.log('그 판이 끝난 뒤 다시 돌리거나, 정말 겹쳐도 되면 --force 를 준다.');
      process.exit(2);
    }
    console.log(`${C.skip}남아 있던 자물쇠를 치운다${C.off} (프로세스 ${old} 는 죽었다).`);
  } catch (e) { /* 자물쇠가 없다 — 처음 도는 판이다 */ }
  fs.writeFileSync(LOCK, String(process.pid));
  const off = function () { try { fs.unlinkSync(LOCK); } catch (e) {} };
  process.on('exit', off);
  ['SIGINT', 'SIGTERM'].forEach(function (sig) {
    process.on(sig, function () { off(); process.exit(130); });
  });
  return off;
}

lock();                      // 겹쳐 도는 판을 여기서 막는다
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

let durs = {};
try { durs = JSON.parse(fs.readFileSync(DUR, 'utf8')); } catch (e) { durs = {}; }

function run(cmd) {
  const t0 = Date.now();
  const parts = cmd.split(/\s+/);
  /* 한 검사가 멈추면 스윕 전체가 멈춘다. 시간을 끊고 실패로 적는다 —
     '아직 도는 중' 과 '고장' 을 사람이 구분하려고 기다릴 이유가 없다. */
  const r = spawnSync(parts[0], parts.slice(1), { cwd: ROOT, encoding: 'utf8', timeout: 12*60*1000 });
  const out = (r.stdout || '') + (r.stderr || '') + (r.error ? '\n' + r.error.message : '');
  const skip = /^건너뜀:/m.test(out);
  const name = cmd.replace(/^(node|python3)\s+/, '');
  const secs = Math.round((Date.now() - t0) / 100) / 10;
  if (!skip) durs[cmd] = secs;
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

/* ── 빠른 판 ────────────────────────────────────────────────────────────
   2026-08-11, 선생님 결정 #34·#44 — *"검사 116단계가 12분. 선생님이 손으로
   돌리기엔 길다"*, *"판이 12분이라 실패를 늦게 안다"*.

   ⚠ 빠른 판은 **전체 판이 아니다.** 이 저장소가 가장 경계하는 것이 «건너뛴
     것을 초록으로 세는 것» 이라, 여기서는 끝에 반드시 무엇을 안 돌렸는지
     적고 «통과» 라고 말하지 않는다.

   무엇이 빠른지는 **지난번에 잰 값**(tests/durations.json)에서 고른다.
   손으로 목록을 적으면 검사가 늘 때마다 갈라진다. */
const FAST = process.argv.includes('--fast') || process.env.FAST === '1';
const FAST_MAX = Number(process.env.FAST_MAX || 6);   // 초
let plan = steps, held = [];
if (FAST) {
  const known = steps.filter(c => durs[c] != null);
  if (!known.length) {
    console.log('빠른 판을 고를 잰 값이 없습니다 — 이번에는 전부 돌리고 시간을 적어 둡니다.\n');
  } else {
    plan = steps.filter(c => durs[c] == null || durs[c] <= FAST_MAX);
    held = steps.filter(c => !plan.includes(c));
  }
}

console.log(`검사 ${plan.length}개${held.length ? ` (뒤로 미룬 것 ${held.length}개)` : ''}`
  + ` · tests/*.js ${nodeFiles.length}개\n`);
plan.forEach(run);

if (orphan.length) {
  console.log(`\n${C.skip}CI 에 걸리지 않은 검사 파일${C.off} — 만들어 놓고 안 돌리면 없는 것과 같습니다`);
  orphan.forEach(f => console.log(`  tests/${f}`));
}

try { fs.writeFileSync(DUR, JSON.stringify(Object.keys(durs).sort()
  .reduce((o, k) => (o[k] = durs[k], o), {}), null, 1) + '\n'); } catch (e) {}

console.log(`\n통과 ${ok} · 건너뜀 ${skipped} · 실패 ${failed}`);
if (held.length) {
  /* 여기가 빠른 판의 존재 이유이자 위험이다. **안 돌린 것을 안 적으면**
     빠른 판이 초록일 때 사람이 다 됐다고 믿는다. */
  const mins = Math.round(held.reduce((s2, c) => s2 + (durs[c] || 0), 0) / 6) / 10;
  console.log(`${C.skip}\n빠른 판입니다 — ${held.length}개(약 ${mins}분)를 안 돌렸습니다. 통과가 아닙니다.${C.off}`);
  held.slice(0, 8).forEach(c => console.log(`${C.dim}  ${c.replace(/^(node|python3)\s+/, '')}  ${durs[c]}초${C.off}`));
  if (held.length > 8) console.log(`${C.dim}  … 그리고 ${held.length - 8}개${C.off}`);
  console.log(`${C.dim}  전부 돌리려면 --fast 를 빼고 돌립니다.${C.off}`);
}
if (skipped) {
  /* 여기가 이 파일의 존재 이유다. 건너뛴 것을 초록으로 적으면, 브라우저에서만
     드러나는 고장이 커밋 여러 개를 지나간다 — 실제로 그랬다. */
  console.log(`${C.skip}\n주의: ${skipped}개가 브라우저가 없어 건너뛰었습니다. 통과한 것이 아닙니다.${C.off}`);
  console.log(`${C.dim}  전부 돌리려면: (저장소 루트에서 python3 -m http.server 8931 을 띄운 뒤)`);
  console.log(`  PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/run.js${C.off}`);
}
if (orphan.length) console.log(`${C.skip}CI 에 안 걸린 파일 ${orphan.length}개${C.off}`);

/* 빠른 판에서는 «CI 에 안 걸린 파일» 로 빨간불을 켜지 않는다. 안 돌린 것이
   있는 판이라 그 셈이 어차피 반쪽이다. */
process.exit(failed || (!FAST && orphan.length) ? 1 : 0);
