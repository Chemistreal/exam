#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""인쇄해서 쓰는 화면에 **인쇄 규칙**이 있는지 보고, 없으면 넣는다.

왜 필요한가
-----------
해설지·문제지는 화면으로도 보지만 **종이로 나가는 것이 본업**이다. 그런데
인쇄 규칙이 없으면 이런 일이 생긴다.

  · 바탕색(#faf8f4)이 A4 한 장을 통째로 덮는다 — 잉크를 먹고 글씨가 흐려진다
  · 문항이 페이지 경계에서 반으로 잘린다 — 발문은 앞장, 보기는 뒷장
  · 화면용 거르개 단추가 그대로 찍힌다 — 종이에서는 누를 수 없는 것이다
  · 여백이 브라우저 기본값이라 인쇄할 때마다 다르다

재어 보니 exam 의 인쇄용 화면 216장 중 **211장**에 인쇄 뜻(`@media print`·
`@page`)이 아예 없었다. DT 는 0장이다 — OMR 이 처음부터 `@page` 로 지어져
있다. 같은 저장소 안에서 한쪽은 되어 있고 한쪽은 안 되어 있었다.

⚠ 해설지 생성기(gen_sol_page.py)에는 이미 인쇄 규칙이 있다. 그런데 옛 수작업
해설지 76장은 그 생성기가 만든 것이 아니라서 `--check` 가 **건너뛰고 있었다**
(생성기 표식이 없으면 견주지 않는다). 검사 밖에 있던 자리다.

강의록 125장은 인쇄하면 **제목이 사라진다**
-------------------------------------------
강의록(lec-*.html)은 수업 시간에 나눠 주는 종이가 본업이다. 그런데 125장
전부에 인쇄 규칙이 없었고, 그 중에서도 이것이 제일 나쁘다.

    header{background:linear-gradient(180deg,#0E5A4C,#0b4a3f);color:#fff}
    .sec__no{background:var(--teal);color:#fff}

브라우저는 인쇄할 때 **배경을 기본으로 안 찍는다**(잉크를 아끼려고 그런다.
'배경 그래픽' 을 사람이 따로 켜야 나온다). 그러면 초록 배경은 안 찍히고
그 위의 흰 글씨만 남는다 — **흰 종이에 흰 글씨**다.

  · 강의록 제목(header h1) 이 통째로 안 보인다 — 125장 전부
  · 절 번호(.sec__no) 가 전부 안 보인다 — 601곳
  · 단계 번호(.steps li::before) 7장, 흐름도 마디(.flow .node) 2장

화면으로 보면 멀쩡하니 아무도 몰랐다. 종이에서만 사라진다.

무엇을 넣나
-----------
화면에는 **아무 영향이 없다.** `@page` 와 `@media print` 는 종이에서만 산다.

문제지·해설지(sol-·paper-):

    @page{size:A4;margin:14mm 12mm}
    @media print{
      body{background:#fff}     잉크를 아끼고 글씨가 진해진다
      .q{break-inside:avoid}    문항이 페이지에서 반으로 안 잘린다
      .filt{display:none}       화면용 거르개는 종이에 안 찍는다
    }

강의록(lec-):  위에 더해, 색 배경 위의 흰 글씨를 **검은 글씨 + 테두리**로
바꾼다. 배경이 안 찍혀도 읽힌다.

    @media print{
      header{background:#fff;color:#000;border-bottom:2px solid #000}
      .sec__no{background:#fff;color:#000;border:1.5px solid #000}
    }

`.q`·`.filt` 는 이 저장소의 해설지·문제지가 실제로 쓰는 이름이다(문항 3,720곳).
없는 화면에서는 그냥 안 걸린다.

    실행:  python3 tools/print_styles.py            # 세기만
           python3 tools/print_styles.py --write    # 없는 곳에 넣는다
           python3 tools/print_styles.py --check    # 빠진 곳이 있으면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HAS_INTENT = re.compile(r'@media\s+print|@page\b', re.I)
STYLE_END = re.compile(r'</style>', re.I)

# 문제지·해설지 — 문항이 페이지에서 안 잘리게, 화면용 거르개는 안 찍게.
BLOCK_PAPER = (
    "\n/* 인쇄 — 종이에서만 산다. 화면은 하나도 안 바뀐다. */\n"
    "@page{size:A4;margin:14mm 12mm}\n"
    "@media print{body{background:#fff}.q{break-inside:avoid}.filt{display:none}}\n"
)

# 강의록 — 배경이 안 찍혀도 읽히게. 흰 글씨를 검은 글씨 + 테두리로 바꾼다.
# ⚠ 이 규칙은 원래 규칙보다 **뒤에** 놓여야 이긴다(선택자 무게가 같다).
#   그래서 </style> 바로 앞에 넣는다.
BLOCK_LEC = (
    "\n/* 인쇄 — 종이에서만 산다. 화면은 하나도 안 바뀐다.\n"
    "   브라우저는 인쇄할 때 배경을 기본으로 안 찍는다. 색 배경 위의 흰 글씨는\n"
    "   그래서 흰 종이에 흰 글씨가 된다 — 제목과 절 번호가 통째로 사라졌다. */\n"
    "@page{size:A4;margin:15mm 13mm}\n"
    "@media print{\n"
    "  body{background:#fff}\n"
    "  header{background:#fff;color:#000;border-bottom:2px solid #000;padding:8mm 0 5mm}\n"
    "  header .logo,header .sub{color:#333;opacity:1}\n"
    "  .sec__no{background:#fff;color:#000;border:1.5px solid #000}\n"
    "  .steps li::before,.flow .node{background:#fff;color:#000;border:1.5px solid #000}\n"
    "  .back{display:none}\n"
    "  .sec,.key,.trap,.eg,.fm{break-inside:avoid}\n"
    "}\n"
)

# 인쇄가 본업인 화면. 이름으로 가른다 — 이 저장소는 이름이 곧 갈래다.
FAMILIES = (
    (('sol-', 'paper-'), BLOCK_PAPER),
    (('lec-',), BLOCK_LEC),
)
PRINTABLE = tuple(p for pre, _ in FAMILIES for p in pre)


# 강의록에서 '흰 글씨를 되돌렸는가'. 종이에서 제목이 살아 있는지의 기준이다.
WHITE_FIXED = re.compile(r'header\s*\{[^}]*background:\s*#fff', re.I)


def block_for(name):
    for pre, blk in FAMILIES:
        if name.startswith(pre):
            return blk
    return None


def targets():
    for f in sorted(os.listdir(ROOT)):
        if f.endswith('.html') and f.startswith(PRINTABLE):
            yield os.path.join(ROOT, f)


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    have = miss = done = 0
    names = []
    for p in targets():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        base = os.path.basename(p)
        blk = block_for(base)
        if HAS_INTENT.search(src):
            # 인쇄 뜻은 있다. 그런데 강의록은 그것만으로 모자란다 — 색 배경 위의
            # 흰 글씨를 되돌려 놓지 않으면 종이에서 제목이 사라진 채 그대로다.
            if blk is BLOCK_LEC and not WHITE_FIXED.search(src):
                miss += 1
                names.append(base + ' (흰 글씨 되돌림 없음)')
            else:
                have += 1
            continue
        m = STYLE_END.search(src)
        if not m:
            # <style> 이 없는 화면에는 넣을 자리가 없다. 세기만 한다.
            miss += 1
            names.append(base + ' (style 없음)')
            continue
        miss += 1
        names.append(base)
        if write:
            open(p, 'w', encoding='utf-8').write(src[:m.start()] + blk + src[m.start():])
            done += 1

    if write:
        print(f'인쇄 규칙을 넣었다: {done}장 (이미 있던 것 {have}장)')
        return 0
    print(f'인쇄 규칙 있음 {have}장 · 없음 {miss}장')
    for n in names[:8]:
        print('   ' + n)
    if len(names) > 8:
        print(f'   … 외 {len(names)-8}장')
    if check and miss:
        print('\nFAIL 인쇄해서 쓰는 화면에 인쇄 규칙이 없다 — '
              'python3 tools/print_styles.py --write')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
