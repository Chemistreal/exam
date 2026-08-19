/* ============================================================
   weak60.html 이 final.html 에서 가져간 조각이 갈라지지 않았다

   weak60.html 은 final.html 의 채점 규칙(okq·allc·accSet)과 명단 열쇠
   (PFX·cohortKey·subs)를 **그대로 옮겨 쓴다.** 한 파일에 두고 부를 수가
   없기 때문이다 — 이 저장소의 앱은 바깥 .js 를 안 건다(첫 그림이 늦는다).

   그래서 갈라질 수 있다. 갈라지면 **같은 학생이 두 화면에서 다른 점수를
   받는다.** 성적표는 48점인데 60제 채점은 47점인 식이다. 그런 어긋남은
   눈으로 못 찾는다 — 복수정답이 걸린 문항 하나에서만 나기 때문이다.

   그래서 여기서 잰다. weak60.html 의 두 표지 사이에 있는 줄을 하나씩
   final.html 에서 **글자 그대로** 찾는다. 못 찾으면 죽는다.
   고칠 일이 있으면 final.html 을 고치고 여기로 옮긴다. 반대로 하지 않는다.
   ============================================================ */
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let fail = 0;
const chk = (n, ok, info) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n + (ok ? '' : '   ' + info));
  if (!ok) fail++;
};

const w60 = fs.readFileSync(path.join(ROOT, 'weak60.html'), 'utf8');
const fin = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');

const m = w60.match(/\/\* ==W60-SHARED-BEGIN== \*\/\n([\s\S]*?)\n\/\* ==W60-SHARED-END== \*\//);
chk('옮겨 온 자리에 표지가 둘 다 있다', !!m, '표지를 못 찾았다');
if (!m) { console.log('\n결과: 실패 ' + fail + '건'); process.exit(1); }

const lines = m[1].split('\n');
chk('옮겨 온 줄이 넉넉히 있다', lines.length >= 40, '옮겨 온 줄 ' + lines.length);

/* 빈 줄과 주석만인 줄은 건너뛴다 — 옮기면서 줄바꿈이 달라질 수 있고,
   그것까지 걸면 검사가 사람을 괴롭히기만 한다. 코드는 글자 그대로 본다. */
const isNoise = s => !s.trim() || /^\s*(\/\/|\/\*|\*)/.test(s.trim());
const missing = [];
lines.forEach((ln, i) => {
  if (isNoise(ln)) return;
  if (fin.indexOf(ln) < 0) missing.push((i + 1) + ': ' + ln.trim().slice(0, 70));
});
chk('옮겨 온 줄이 final.html 에 글자 그대로 다 있다', missing.length === 0,
    missing.slice(0, 4).join('  |  ') + (missing.length > 4 ? ' … 그 밖 ' + (missing.length - 4) + '줄' : ''));

/* 채점의 뼈대 넷은 이름을 대고 따로 본다 — 위 검사가 통째로 지나가더라도
   이 넷 가운데 하나가 빠졌다면 그건 옮기다 흘린 것이다. */
['const okq=', 'const allc=', 'const accSet=', 'const nameKey=', 'const cohortKey=', 'function subs(id)']
  .forEach(k => chk('「' + k + '」 이 옮겨 와 있다', m[1].indexOf(k) >= 0, ''));

/* PFX 는 final.html 에서 MINP 와 한 줄에 묶여 있어 그대로 못 옮긴다.
   값이 같은지만 본다 — 갈리면 60제 자리에 명단이 아예 안 보인다. */
const fp = (fin.match(/PFX\s*=\s*'([^']+)'/) || [])[1];
const wp = (w60.match(/const PFX\s*=\s*'([^']+)'/) || [])[1];
chk('명단 열쇠(PFX)가 두 파일에서 같다', !!fp && fp === wp, 'final=' + fp + ' · weak60=' + wp);

/* 옮긴 것이지 남겨 둔 것이 아니다 — final.html 에 60제 만드는 함수가
   남아 있으면 두 곳에서 고치게 된다. */
['function weak60Plan', 'function weakScan', 'async function weak60Fill', 'function _w60paper']
  .forEach(k => chk('final.html 에 「' + k + '」 이 남아 있지 않다', fin.indexOf(k) < 0, ''));
chk('final.html 이 weak60.html 로 길을 낸다', /href="weak60\.html/.test(fin), '');

/* ── 문고리가 걸려 있다 ──────────────────────────────────
   이 화면에는 **반 전체 명단**이 뜨고, 누르면 **정답이 실린 해설 Word** 가
   나온다. 성적표보다 더 열어 두면 안 되는 자리다. 그런데 열쇠칸이나 코드가
   final.html 과 갈리면 선생님이 성적표에서 넣고 여기서 또 넣게 된다. */
const fg = fin.match(/var KEY = '([^']+)', CODE = '([^']+)'/);
const wg = w60.match(/var KEY = '([^']+)', CODE = '([^']+)'/);
chk('60제 자리에도 문고리가 걸려 있다', !!wg, '');
chk('열쇠칸과 코드가 성적표와 같다', !!wg && !!fg && wg[1] === fg[1] && wg[2] === fg[2],
    (wg ? wg.slice(1, 3).join('/') : '없음') + ' vs ' + (fg ? fg.slice(1, 3).join('/') : '없음'));
/* final.html 의 학부모 예외(#r=)를 같이 옮겨 오면 안 된다 — 이 화면에는
   학생·학부모에게 줄 것이 하나도 없다. */
chk('학부모 예외를 옮겨 오지 않았다', !/__sharedReport/.test(w60), '');

/* ── 표가 종이 밖으로 나가지 않는다 ──────────────────────
   A4 는 11906 DXA 이고 좌우 여백이 1000 씩이라 본문에 쓸 수 있는 폭은
   9906 이다. 칸 너비의 합이 이 값을 넘으면 표가 오른쪽으로 삐져나가고,
   **맨 오른쪽 칸이 통째로 잘린다.** 처음에 11200 으로 두었더니 표지의
   복원 코드가 반쯤 잘려 나갔다 — 찍어 보고서야 알았다. 눈으로 볼 일이
   아니라 여기서 센다. */
const USABLE = 11906 - 1000 - 1000;
const wide = [];
const re = /K\.table\(\s*(?:\[[\s\S]*?\]|\w+)\s*,\s*\[([\d,\s]+)\]\s*\)/g;
let mm, tables = 0;
while ((mm = re.exec(w60))) {
  tables++;
  const sum = mm[1].split(',').map(Number).reduce((a, c) => a + c, 0);
  if (sum > USABLE) wide.push(sum + ' (' + mm[1].trim().slice(0, 40) + ')');
}
chk('표 너비를 잰 자리가 있다', tables >= 5, '찾은 표 ' + tables);
chk('어떤 표도 A4 본문 폭(' + USABLE + ')을 넘지 않는다', wide.length === 0, wide.join(' · '));

console.log('\n결과: ' + (fail ? '실패 ' + fail + '건' : '전부 통과'));
process.exit(fail ? 1 : 0);
