#!/usr/bin/env python3
"""**오개념 카탈로그와 강의의 함정이 같은 말을 하는지** 본다.

이 저장소에는 오개념이 세 군데 적혀 있다.

    ① `misconception-catalog.html`  125개념마다 한 줄씩 · 여덟 유형으로 갈라
    ② 강의 125편의 `함정` 칸           학생이 읽는 자리
    ③ 오답 카드의 오개념 한 줄         `om_cover.py` 가 비었는지만 본다

셋이 따로 자라면, 카탈로그는 아는데 강의는 말 안 해 주는 오개념이 생긴다.
실제로 다섯 개념(036·043·061·097·105)이 그랬다 — 카탈로그에는 있는데
강의에 함정 칸이 없었다.

여기서 보는 것은 **있는지 없는지**뿐이다. 두 글이 같은 뜻인지까지는
기계가 못 판정한다(넷째 원칙). 그건 검수 대장(`review_queue.py`)으로 간다.

    python3 tools/mis_sync.py           # 어긋난 개념
    python3 tools/mis_sync.py --check   # 하나라도 있으면 빨간불
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, 'misconception-catalog.html')


def catalog():
    """개념 번호 → 카탈로그가 아는 오개념 줄."""
    s = open(CAT, encoding='utf-8').read()
    m = re.search(r"=\s*\{'001':\[\[[\s\S]*?\]\}\s*,\s*TYPES", s)
    if not m:
        return {}
    got = {}
    for k, v in re.findall(r"'(\d{3})':\[(.*?)\](?=,'\d{3}':|\}\s*,\s*TYPES)", m.group(0)):
        got[k] = re.findall(r"\['([^']*)','([^']*)','([^']*)'(?:,'([^']*)')?\]", v)
    return got


def traps():
    """개념 번호 → 그 강의의 함정 칸 수."""
    got = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'lec-*.html'))):
        n = os.path.basename(f).split('-')[1]
        s = open(f, encoding='utf-8').read()
        got[n] = len(re.findall(r'<div class="trap">', s))
    return got


def main():
    check = '--check' in sys.argv
    cat, tr = catalog(), traps()
    print('카탈로그 개념 %d개 · 강의 %d편' % (len(cat), len(tr)))

    no_lec = sorted(k for k in cat if k not in tr)
    no_trap = sorted(k for k in cat if tr.get(k) == 0)
    no_cat = sorted(k for k in tr if k not in cat)

    if no_lec:
        print('\n카탈로그에 있는데 강의가 없는 개념 %d개: %s' % (len(no_lec), ' '.join(no_lec)))
    if no_trap:
        print('\n카탈로그는 아는데 강의에 함정 칸이 없는 개념 %d개' % len(no_trap))
        for k in no_trap:
            print('   %s · %s' % (k, cat[k][0][0] if cat[k] else ''))
    if no_cat:
        print('\n강의는 있는데 카탈로그에 없는 개념 %d개: %s' % (len(no_cat), ' '.join(no_cat)))
    if not (no_lec or no_trap or no_cat):
        print('\n125개념이 세 자리에서 같은 목록을 든다.')

    bad = bool(no_lec or no_trap or no_cat)
    if check:
        print('\n' + ('FAIL' if bad else 'PASS'))
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
