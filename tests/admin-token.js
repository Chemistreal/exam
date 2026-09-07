/* ============================================================
   관리 열쇠 — 회귀 테스트
   ------------------------------------------------------------
   이 창구는 열쇠 없이 열려 있었다. 주소는 공개 저장소의 화면 파일에 그대로
   박혀 있으므로, `?action=all` 한 번이면 전교생 이름·학교·학년·전 회차
   답안이 나온다. 미성년자 명단이다.

   그렇다고 열쇠를 그냥 켜면 이미 나간 것들이 그 자리에서 죽는다 —
   학부모에게 보낸 성적표 링크가 부르는 것도 같은 창구다. 그래서 규칙을
   이렇게 갈랐다:

   - **이름이 실려 나오는 읽기**(all·history)와 **시트를 바꾸는 동작**만 막는다
   - `list`·`cohort`·학생 제출(doPost)은 **안 막는다** — 보낸 링크가 살아야 한다
   - 스크립트 속성 `ADMIN_TOKEN` 을 **안 두면 예전 그대로 돈다** — 켜는 시점은
     선생님이 고르신다

   여기서 지키는 것:
   - 막는 목록에 이름 실린 읽기와 바꾸는 동작이 다 들어 있다
   - 막는 목록에 list·cohort 가 **없다**(이미 보낸 링크가 안 죽는다)
   - 열쇠를 안 두면 아무것도 안 막힌다
   - 열쇠를 두면 없는·틀린 열쇠는 막히고 맞는 열쇠는 지나간다
   - 화면은 열쇠가 있을 때만 붙여 보낸다
   - 열쇠가 저장소 파일에 적혀 있지 않다

   실행:  node tests/admin-token.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');
const FIN = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) fail++;
  console.log((ok ? '  ok   ' : '  FAIL ') + n +
    (ok ? '' : `\n         받은 것: ${JSON.stringify(got)}\n         바란 것: ${JSON.stringify(want)}`));
};

/* ── .gs 의 문지기만 오려 온다 ──────────────────────────────────────── */
let PROP = null;
const ctx = vm.createContext(require('./_gasenv')({
  PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k === 'ADMIN_TOKEN' ? PROP : null) }) },
  ContentService: {
    MimeType: { JAVASCRIPT: 'js', JSON: 'json' },
    createTextOutput: t => ({ body: t, setMimeType() { return this; } }),
  },
}));
for (const re of [/var ADMIN_ACTIONS = \[[\s\S]*?\];/,
                  /function _cbName_\([\s\S]*?\n\}/,
                  /function _jsonOut_\([\s\S]*?\n\}/,
                  /function _adminToken_\([\s\S]*?\n\}/,
                  /function _adminOk_\([\s\S]*?\n\}/]) {
  const m = GAS.match(re);
  if (!m) { console.log('  FAIL .gs 에서 못 찾았다: ' + re); fail++; }
  else vm.runInContext(m[0], ctx);
}
const ACTIONS = vm.runInContext('ADMIN_ACTIONS', ctx);
const ok = (p) => vm.runInContext('_adminOk_(' + JSON.stringify(p) + ')', ctx);

console.log('무엇을 막는가');
for (const a of ['history', 'all', 'rename', 'editRow', 'deleteRow', 'deleteName',
                 'dedupe', 'recompute', 'purgeTest']) {
  chk('막는다: ' + a, ACTIONS.indexOf(a) >= 0, true);
}
console.log('\n무엇을 막지 않는가 — 이미 보낸 링크가 부르는 것들');
for (const a of ['list', 'cohort']) {
  chk('안 막는다: ' + a, ACTIONS.indexOf(a) >= 0, false);
}
/* doPost 는 doGet 의 문을 아예 안 지난다 — 학생 제출이 열쇠를 요구하면
   시험 자체가 못 돈다. 문지기가 doPost 안에 들어가지 않았는지 본다. */
const post = (() => {
  /* doPost 의 몸통만 오려 낸다 — 괄호를 세어 닫는 자리를 찾는다.
     doPost 부터 doGet 까지를 통째로 자르면 그 사이에 있는 문지기 정의가
     딸려 들어와 검사가 늘 어긋난다. */
  const i = GAS.indexOf('function doPost(e) {');
  let d = 0;
  for (let j = i; j < GAS.length; j++) {
    if (GAS[j] === '{') d++;
    else if (GAS[j] === '}' && --d === 0) return GAS.slice(i, j + 1);
  }
  return GAS.slice(i);
})();
chk('학생 제출길에는 문지기가 없다', /_adminOk_|ADMIN_ACTIONS/.test(post), false);

console.log('\n열쇠를 안 두면 — 오늘 그대로');
PROP = null;
chk('열쇠 없이도 지나간다', ok({ action: 'all' }), true);
PROP = '';
chk('빈 값이어도 지나간다', ok({ action: 'all' }), true);

console.log('\n열쇠를 두면');
PROP = 's3cr3t-key';
chk('안 보내면 막힌다', ok({ action: 'all' }), false);
chk('틀리면 막힌다', ok({ action: 'all', token: 'nope' }), false);
chk('맞으면 지나간다', ok({ action: 'all', token: 's3cr3t-key' }), true);
chk('앞뒤 공백은 다른 열쇠다', ok({ action: 'all', token: ' s3cr3t-key ' }), false);

/* 문지기가 doGet 어귀 한 자리에만 있는가 — 흩어 두면 새 동작을 만들면서
   빠뜨린다. */
console.log('\n문지기가 한 자리인가');
const gets = GAS.split('\n').map((l, i) => [i + 1, l])
  .filter(([, l]) => /!_adminOk_\(/.test(l));
chk('가르는 자리가 하나뿐이다', gets.length, 1);

console.log('\n화면 쪽');
chk('열쇠가 있을 때만 붙인다', /if\(tk && !params\.token\)/.test(FIN), true);
chk('열쇠를 localStorage 에 둔다', /localStorage\.getItem\(ADMIN_TOKEN_KEY\)/.test(FIN), true);
chk('열쇠가 필요하다고 하면 물어본다', /needToken/.test(FIN), true);

/* 열쇠를 파일에 적으면 그 순간 열쇠가 아니다. 저장소 어디에도 없어야 한다. */
console.log('\n열쇠가 저장소에 적혀 있지 않은가');
const written = [];
for (const f of ['final.html', 'admin.html', 'index.html', 'hub.html',
                 'grade-j0.html', 'AppsScript-Code.gs']) {
  const src = fs.readFileSync(path.join(ROOT, f), 'utf8');
  /* `ADMIN_TOKEN` 이라는 **이름**은 적혀 있어도 된다. 값을 박은 자리를 찾는다. */
  if (/ADMIN_TOKEN\s*[=:]\s*['"][^'"]+['"]/.test(src)) written.push(f);
  if (/setAdminToken\(\s*['"][^'"]+['"]\s*\)/.test(src)) written.push(f);
}
chk('열쇠 값을 박아 둔 파일이 없다', written, []);

console.log(fail ? `\n${fail}건 어긋났다` : '\n다 맞다');
process.exit(fail ? 1 : 0);
