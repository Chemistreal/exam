/* ============================================================
   색은 눈이 아니라 자로 정한다 — 두 앱이 갈리지 않게
   ------------------------------------------------------------
   이 검사가 왜 있나. `--muted` 가 #8a8578 이었고 종이색 위에서 3.52:1 이라
   본문 글씨 기준(4.5:1)에 못 미쳤다. 통합 셸(hub.html)에서는 그것을 재서
   #6f6a5e 로 고쳤는데, **파이널 앱(final.html)에는 옛 값이 그대로 남아
   있었다.** 같은 팔레트를 쓰는 두 파일이 조용히 갈렸고, 한쪽만 읽히기
   어려운 채로 학부모에게 나갔다.

   눈으로 보면 "좀 흐린가?" 로 끝난다. 숫자로 박아 두면 되돌아가지 않는다.

   ⚠ 대비는 **글씨가 실제로 얹히는 바탕** 위에서 재야 한다. 종이색 위에서만
   재면 옅은 옥색·분홍 카드 위에서 4.5 를 못 넘기는 것을 놓친다.

   기준(WCAG 2.1 AA)
   - 본문 글씨 4.5:1
   - 큰 글씨(24px 이상, 또는 18.66px 이상 굵게) 3:1
   - 그림·테두리 3:1

   실행:  node tests/contrast.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

function lum(hex) {
  const h = hex.replace('#', '');
  const a = [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255)
    .map(v => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}
function ratio(a, b) {
  const x = lum(a), y = lum(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}
function varOf(src, name) {
  const m = src.match(new RegExp('--' + name + ':\\s*(#[0-9A-Fa-f]{3,8})'));
  return m ? m[1] : null;
}

const FINAL = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
const HUB = fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8');

console.log('── 두 앱이 같은 색을 쓴다 ──');
{
  /* 이 검사의 존재 이유. 한쪽만 고치면 여기서 걸린다. */
  const a = varOf(FINAL, 'muted'), b = varOf(HUB, 'muted');
  console.log('  final --muted ' + a + ' · hub --muted ' + b);
  chk('흐린 글씨색이 두 앱에서 같다', (a || '').toLowerCase(), (b || '').toLowerCase());
}

console.log('\n── 글씨가 실제로 얹히는 바탕 위에서 잰다 ──');
{
  /* 종이색 위에서만 재면 옅은 카드 위에서 못 넘기는 것을 놓친다 —
     실제로 그렇게 놓치고 있었다. */
  const BG = {
    '종이':   varOf(FINAL, 'cream') || '#FBFAF6',
    '흰색':   '#FFFFFF',
    '통과칸': varOf(FINAL, 'ok-bg') || '#eef5f2',
    '미달칸': varOf(FINAL, 'no-bg') || '#f7ece7',
  };
  ['muted', 'ink-2', 'ink'].forEach(name => {
    const c = varOf(FINAL, name);
    if (!c) { chk('--' + name + ' 가 있다', false, true); return; }
    Object.keys(BG).forEach(k => {
      const r = ratio(c, BG[k]);
      chk('--' + name + ' · ' + k + ' 위 ' + r.toFixed(2) + ':1', r >= 4.5, true);
    });
  });
}

console.log('\n── 강조색은 그림 기준(3:1)까지는 지킨다 ──');
{
  /* 놋쇠·옥색은 테두리·막대에 쓴다. 본문 글씨로 쓰지 않는 대신 3:1 은 넘겨야
     한다 — 안 넘기면 테두리가 보이지 않아 칸이 이어져 보인다. */
  const paper = varOf(FINAL, 'cream') || '#FBFAF6';
  [['brass', 3], ['teal', 4.5], ['ms', 3]].forEach(([name, need]) => {
    const c = varOf(FINAL, name);
    if (!c) { chk('--' + name + ' 가 있다', false, true); return; }
    const r = ratio(c, paper);
    chk('--' + name + ' · 종이 위 ' + r.toFixed(2) + ':1 (필요 ' + need + ')', r >= need, true);
  });
}

console.log('\n── 학부모가 휴대폰으로 읽는다 ──');
{
  /* 재어 보니 10~10.5px 이 열세 군데였다. 바닥을 정하고 지킨다. */
  const small = (FINAL.match(/font-size:(\d+(?:\.\d+)?)px/g) || [])
    .map(x => Number(x.replace(/[^\d.]/g, ''))).filter(n => n < 11);
  console.log('  11px 미만 ' + small.length + '개' + (small.length ? ' · ' + small.slice(0, 8).join(',') : ''));
  chk('11px 미만 글씨가 없다', small.length, 0);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
