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

console.log('\n── 색을 못 봐도 읽힌다 ──');
{
  /* 적록색약은 남학생 스무 명 중 한 명꼴이다. 성적표에 이런 문장들이 있었다:

       "또래도 많이 틀린 문항(빨강)이 개념 보강 1순위입니다."
       "색은 현재 숙달도(초록 안정·노랑 보통·빨강 약함·회색 표본 부족)입니다."
       "빨간 영역부터 메우면 위층이 함께 풀립니다."

     색을 못 보면 **문장 자체가 쓸모없다.** 적록색약 필터를 씌우고 화면을 찍어
     보고서야 알았다 — 팔레트 대비만 재서는 안 나온다.

     ⚠ 화학 내용에는 색 이름이 정당하게 나온다("빨강보다 낮은 진동수=적외선").
     그래서 색 이름 전부를 막지 않고, **길잡이 문장에서 색이 유일한 열쇠로
     쓰이던 자리**만 못 박는다. */
  const 색열쇠 = [
    ['(빨강)', /틀린 문항\(빨강\)/],
    ['빨간 영역부터', /빨간 영역부터/],
    /* ⚠ 주석에 옛 문장을 인용해 두었다. 주석까지 잡으면 자가 거짓말을 한다 —
       화면에 실제로 찍히는 꼴(…)입니다.) 만 본다. */
    ['색은 현재 숙달도(…)입니다', /색은 현재 숙달도\([^)]*\)입니다/],
  ];
  색열쇠.forEach(([n, re]) => chk('길잡이가 색으로만 가리키지 않는다 · ' + n, re.test(FINAL), false));
  /* 그 대신 글자로 적혀 있어야 한다. 지도 칸에 숙달도 낱말을 넣는 자리다. */
  chk('선수 개념 지도가 칸 안에 숙달도를 적는다',
      /stOf\s*=\s*d\s*=>/.test(FINAL) && /reliable\(d\)\?sb\[d\]\+'% · ':''\)\+stOf\(d\)/.test(FINAL), true);
}

console.log('\n── 색 바탕 위의 글씨 ──');
{
  /* '옥색 배경에 흰 글씨' 처럼 **바탕색을 전제로 박아 둔 글자색**이 곳곳에
     있었다(#8a3a1d · #FBF0EA · #fff …). 바탕을 조금만 손대도 글씨가 안 읽히게
     되는데, 어디를 같이 고쳐야 하는지는 아무 데도 안 적혀 있었다. 이름을 붙여
     모으고 여기서 잰다.

     ⚠ `#fff` 처럼 **세 자리로 적은 색**이 있다(--paper·--on-teal 이 그렇다).
       lum() 은 여섯 자리를 전제하므로 그대로 넣으면 NaN 이 나오고, NaN 이면
       비교가 **조용히 통과한다** — 실제로 처음에 그렇게 나왔다. 펴서 넣는다. */
  const hex6 = h => {
    if (!h) return h;
    const v = h.replace('#', '');
    return '#' + (v.length === 3 ? v.split('').map(c => c + c).join('') : v);
  };
  const V = name => hex6(varOf(HUB, name));

  const r1 = ratio(V('on-teal'), V('teal'));
  console.log('  옥색 바탕 위 글씨 ' + r1.toFixed(2));
  chk('옥색 바탕 위 글씨가 읽힌다', r1 >= 4.5, true);

  /* '통과' 배지 글씨는 **배지 바탕(9% 초록) 위**에서 재야 한다. 종이 위에서만
     재면 안 나오는 값이고, 그래서 4.15:1 로 기준(4.5)에 못 미치던 것을 여태
     아무도 몰랐다. --ok-ink 로 고쳤다. */
  const over = (fg, tint, alpha, under) => {
    const p = h => [0, 2, 4].map(i => parseInt(hex6(h).slice(1).substr(i, 2), 16));
    const a = p(tint), b = p(under);
    const mix = a.map((v, i) => Math.round(v * alpha + b[i] * (1 - alpha)));
    return ratio(fg, '#' + mix.map(v => v.toString(16).padStart(2, '0')).join(''));
  };
  const r2 = over(V('ok-ink'), '#2F7A5A', 0.09, V('paper'));
  console.log('  통과 배지 글씨 ' + r2.toFixed(2) + ' (예전 --ok 로는 4.15)');
  chk('통과 배지 글씨가 읽힌다', r2 >= 4.5, true);

  ['ms-ink', 'warn-ink'].forEach(k => {
    const r = ratio(V(k), V('paper'));
    console.log('  ' + k.padEnd(9) + ' ' + r.toFixed(2));
    chk('배지 글씨가 읽힌다 · ' + k, r >= 4.5, true);
  });

  /* 색을 바탕으로 쓰는 자리에 **흰색을 박아 두지 않았는가.** 이 규칙이 없으면
     다음에 또 var(--teal) 위에 #fff 를 적게 된다. */
  chk('옥색 바탕에 흰 글씨를 박아 두지 않았다',
      /background:var\(--teal\)[^}]*color:#fff/.test(HUB.split('<script>')[0]), false);
  /* 이 화면은 **밝은 화면 하나**로 간다(선생님 결정). 그렇다고 이 줄을 지우면
     기기가 어두운 화면일 때 브라우저가 스크롤막대·입력칸을 제멋대로 어둡게
     그려서, 종이색 화면에 검은 막대가 붙는다. */
  chk('밝은 화면이라고 적어 둔다', /color-scheme:\s*light\s*;/.test(HUB), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
