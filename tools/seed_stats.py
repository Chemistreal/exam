#!/usr/bin/env python3
"""index.html 의 두 코호트가 서로 어긋나지 않는지 본다 — SEEDS 와 STATIC_STATS.

셈이 안 맞아 보여서 한 번 파 본 자리다. 기록해 둔다.

    kch1to3   STATIC_STATS.N = 339   SEEDS 줄 443
    kch1to2   STATIC_STATS.N = 144   SEEDS 줄 145
    kch1u1    139 = 139   kch2final 61 = 61   kch2to3 17 = 17

**틀린 것이 아니다.** 둘은 다른 것을 잰다.

    SEEDS[id]          학생 한 명이 영역마다 몇 점인지 적은 줄. 백분위 자리와
                       다음 응시번호(seedCount)에 쓴다. 영역 합계만 있으면 된다
    STATIC_STATS[id]   문항별 정답률·선택지 분포·변별도. 문항 하나하나의 답이
                       온전히 있어야 셈할 수 있다. 그래서 더 좁은 무리다

그러니 늘 `STATIC_STATS.N ≤ SEEDS 줄 수` 여야 한다. 다섯 시험 모두 그렇다.
뒤집히면 둘 중 하나가 낡은 것이니 그때는 진짜 어긋난 것이다.

두 값 다 구글 시트의 원시 답안에서 나온다(tools/regen_seed_cohort.py).
저장소 안에서는 다시 만들 수 없으므로 여기서는 **어긋나지 않는지만** 본다.

    python3 tools/seed_stats.py           # 두 코호트의 크기
    python3 tools/seed_stats.py --check   # 뒤집히면 빨간불 (CI용)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'index.html')


def block(src, name):
    i = src.find('const %s={' % name)
    if i < 0:
        return ''
    k = src.find('{', i)
    depth = 0
    while k < len(src):
        c = src[k]
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
            if depth == 0:
                return src[i:k + 1]
        elif c == '"':
            k += 1
            while k < len(src) and src[k] != '"':
                k += 2 if src[k] == '\\' else 1
        k += 1
    return ''


def main():
    check = '--check' in sys.argv
    src = open(PAGE, encoding='utf-8').read()
    ss, sd = block(src, 'STATIC_STATS'), block(src, 'SEEDS')
    if not ss or not sd:
        print('index.html 에서 두 뭉치를 못 찾았다.')
        return 1 if check else 0

    stats = {k: int(v) for k, v in re.findall(r'"([\w-]+)":\{N:(\d+)', ss)}
    bad = []
    print('  %-12s %8s %10s' % ('시험', '문항통계', '영역벡터'))
    for key, n in stats.items():
        m = re.search(r'"%s":\[(.*?)\]\s*(?:,\s*"|\})' % re.escape(key), sd, re.S)
        rows = len(re.findall(r'\[[^\[\]]*\]', m.group(1))) if m else 0
        mark = ''
        if not m:
            mark = '  ← SEEDS 에 없다'
            bad.append('%s: SEEDS 에 줄이 없다' % key)
        elif n > rows:
            mark = '  ← 뒤집혔다'
            bad.append('%s: 문항통계 %d명인데 영역벡터는 %d줄뿐이다 — 둘 중 하나가 낡았다'
                       % (key, n, rows))
        print('  %-12s %6d명 %8d줄%s' % (key, n, rows, mark))

    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n둘 다 구글 시트의 원시 답안에서 나온다 — tools/regen_seed_cohort.py 로')
        print('다시 뽑아 붙여야 한다. 저장소 안에서는 만들 수 없다.')
        return 1 if check else 0

    print('\n문항통계 무리가 영역벡터 무리 안에 있다 (늘 그래야 한다).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
