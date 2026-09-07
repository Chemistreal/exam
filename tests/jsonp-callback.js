/* ============================================================
   되부를 함수 이름이 아닌 것은 되부르지 않는다 — 회귀 테스트
   ------------------------------------------------------------
   JSONP 응답은 받은 글자를 **그대로 자바스크립트로** 내보낸다. 그래서
   `?action=list&callback=alert(1);//` 같은 주소는 응답 자체가 남의 코드가
   된다. 그 주소는 script.google.com 에서 열리므로, 브라우저는 그것을
   구글 도메인의 코드로 믿는다 — 학생·학부모에게 그 링크 하나만 보내면
   된다.

   앱이 실제로 보내는 것은 언제나 `cb_1234` 꼴의 임시 이름 하나다. 그러니
   함수 이름 모양이 아닌 것은 되부르지 않고 그냥 JSON 으로 돌려준다.
   앱은 아무것도 안 달라지고(모양이 늘 맞다), 남의 코드만 못 실린다.

   여기서 지키는 것:
   - 멀쩡한 이름은 그대로 되부른다(앱이 안 깨진다)
   - 괄호·세미콜론·따옴표·공백이 든 것은 되부르지 않는다
   - 64자를 넘는 이름도 안 받는다
   - .gs 안에 `cb + '('` 를 직접 잇는 자리가 하나도 안 남아 있다

   실행:  node tests/jsonp-callback.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) fail++;
  console.log((ok ? '  ok   ' : '  FAIL ') + n +
    (ok ? '' : `\n         받은 것: ${JSON.stringify(got)}\n         바란 것: ${JSON.stringify(want)}`));
};

/* ── _cbName_ 과 _jsonOut_ 만 오려 온다 ─────────────────────────────── */
const ctx = vm.createContext(require('./_gasenv')({
  ContentService: {
    MimeType: { JAVASCRIPT: 'js', JSON: 'json' },
    createTextOutput: t => ({ body: t, mime: '', setMimeType(m) { this.mime = m; return this; } }),
  },
}));
for (const fn of ['_cbName_', '_jsonOut_']) {
  const m = GAS.match(new RegExp('function ' + fn + '\\([\\s\\S]*?\\n\\}', ''));
  if (!m) { console.log('  FAIL ' + fn + ' 를 .gs 에서 못 찾았다'); fail++; }
  else vm.runInContext(m[0], ctx);
}

const BODY = '{"ok":true}';
const out = cb => vm.runInContext(
  '_jsonOut_(' + JSON.stringify(BODY) + ',' + JSON.stringify(cb) + ')', ctx);

console.log('되부를 이름 검사');
chk('앱이 쓰는 이름은 그대로 되부른다', out('cb_1757203').body, 'cb_1757203({"ok":true})');
chk('밑줄·달러로 시작하는 이름도 받는다', out('$j').body, '$j({"ok":true})');
chk('멀쩡한 이름이면 자바스크립트로 낸다', out('cb1').mime, 'js');

for (const bad of [
  'alert(1);//', 'a=1', 'a b', 'a.b', 'a-b', 'a;b', "a'b", 'a"b', 'a\nb',
  '1cb', '', 'x'.repeat(65), '<script>', 'a)//',
]) {
  chk('되부르지 않는다: ' + JSON.stringify(bad), out(bad).body, '{"ok":true}');
}
chk('안 받는 이름이면 JSON 으로 낸다', out('alert(1);//').mime, 'json');
chk('안 보내면 JSON 으로 낸다', out(null).body, '{"ok":true}');

/* ── 직접 잇는 자리가 안 남아 있는가 ─────────────────────────────────
   _jsonOut_ 을 안 지나고 제 손으로 이어 붙이면 이 검사를 통째로 비껴간다.
   그래서 파일에 그런 자리가 하나도 없어야 한다. */
console.log('\n직접 잇는 자리');
const raw = GAS.split('\n')
  .map((l, i) => [i + 1, l])
  .filter(([, l]) => /cb\s*\+\s*'\('/.test(l) && !/^\s*\*/.test(l));
chk('cb 를 손으로 이어 붙이는 자리가 없다', raw.map(([i]) => i), []);

/* ── 앱이 실제로 만드는 이름이 이 문을 통과하는가 ────────────────────
   문을 좁혀 놓고 앱이 못 지나가면 화면이 통째로 죽는다. 그러니 화면들이
   짓는 이름을 그대로 가져다 대 본다. 이름은 `'__lc'+Date.now()` 처럼
   앞머리 글자 + 숫자로 짓는다 — 앞머리만 봐도 통과 여부가 갈린다. */
console.log('\n화면이 짓는 이름');
for (const f of ['index.html', 'final.html', 'admin.html', 'grade-j0.html', 'hub.html']) {
  const src = fs.readFileSync(path.join(ROOT, f), 'utf8');
  const names = [];
  const re = /\b(?:cb|nm)\s*=\s*'([^']*)'/g;
  let m;
  while ((m = re.exec(src))) names.push(m[1]);
  const bad = names.filter(n => !vm.runInContext('_cbName_(' + JSON.stringify(n) + ')', ctx));
  chk(f + ' 이 짓는 이름이 다 통과한다', bad, []);
}

console.log(fail ? `\n${fail}건 어긋났다` : '\n다 맞다');
process.exit(fail ? 1 : 0);
