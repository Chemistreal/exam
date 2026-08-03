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

무엇을 넣나
-----------
화면에는 **아무 영향이 없다.** `@page` 와 `@media print` 는 종이에서만 산다.

    @page{size:A4;margin:14mm 12mm}
    @media print{
      body{background:#fff}     잉크를 아끼고 글씨가 진해진다
      .q{break-inside:avoid}    문항이 페이지에서 반으로 안 잘린다
      .filt{display:none}       화면용 거르개는 종이에 안 찍는다
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

# 인쇄가 본업인 화면. 이름으로 가른다 — 이 저장소는 이름이 곧 갈래다.
PRINTABLE = ('sol-', 'paper-')

HAS_INTENT = re.compile(r'@media\s+print|@page\b', re.I)
STYLE_END = re.compile(r'</style>', re.I)

BLOCK = (
    "\n/* 인쇄 — 종이에서만 산다. 화면은 하나도 안 바뀐다. */\n"
    "@page{size:A4;margin:14mm 12mm}\n"
    "@media print{body{background:#fff}.q{break-inside:avoid}.filt{display:none}}\n"
)


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
        if HAS_INTENT.search(src):
            have += 1
            continue
        m = STYLE_END.search(src)
        if not m:
            # <style> 이 없는 화면에는 넣을 자리가 없다. 세기만 한다.
            miss += 1
            names.append(os.path.basename(p) + ' (style 없음)')
            continue
        miss += 1
        names.append(os.path.basename(p))
        if write:
            open(p, 'w', encoding='utf-8').write(src[:m.start()] + BLOCK + src[m.start():])
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
