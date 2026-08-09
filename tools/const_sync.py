#!/usr/bin/env python3
"""한 회차 안에서 **문제지와 해설이 같은 상수**를 쓰는지 본다.

저장소 전체를 훑으면 상수가 여러 꼴로 나온다.

    아보가드로수  6.02×10²³(104장) · 6.0×10²³(20) · 6.022×10²³(5) · 6.02214076(1)
    기체상수 R    0.082(71) · 0.0821(26) · 0.082057(2) · 0.08206(3)
    패러데이      96500(33) · 96485(5)

⚠ **이것만으로는 결함이 아니다.** 회차마다 시험지 표지에 적힌 값이 다르고,
  해설은 그 회차의 표지를 따라야 맞다. 실제로 `paper-kch1to2-b`(6.022 · 0.082057)와
  그 해설 `sol-kch1to2-b` 는 같은 값을 쓴다 — 저장소 전체로 보면 튀지만 짝은 맞다.
  전체 통일을 강요하면 **맞는 것을 틀리다고 하는 자**가 된다.

그래서 여기서는 **짝 안에서만** 본다. 같은 회차의 문제지·해설·해설지 전체판이
서로 다른 값을 쓰면 그건 학생이 계산을 못 맞추는 진짜 결함이다.

    python3 tools/const_sync.py           # 회차마다 어떤 값을 쓰나
    python3 tools/const_sync.py --check   # 한 회차 안에서 갈리면 빨간불
"""
import collections
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, 'tools', 'const_sync.json')

# 값이 여러 자리에 적히고, 어긋나면 계산이 달라지는 것들.
CONST = {
    '아보가드로수': re.compile(r'6\.0\d*\s*×\s*10²³'),
    '기체상수 R(L·atm)': re.compile(r'0\.082\d*'),
    '기체상수 R(J)': re.compile(r'8\.31\d*'),
    '패러데이': re.compile(r'\b964\d\d\b|\b96,?500\b'),
    '플랑크': re.compile(r'6\.6\d+\s*×\s*10⁻³⁴'),
}


def text(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'<script[\s\S]*?</script>', '', s)
    s = re.sub(r'<style[\s\S]*?</style>', '', s)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))


def exam_of(name):
    """한 회차에 딸린 화면을 한 이름으로 모은다."""
    n = os.path.basename(name)[:-5]
    for pre in ('sol-final-', 'sol-', 'paper-'):
        if n.startswith(pre):
            n = n[len(pre):]
            break
    # `sol-jmchc-13-full` 과 `sol-final-jmchc-13` 은 같은 회차의 두 판본이다.
    return re.sub(r'-full$', '', n)


def main():
    check = '--check' in sys.argv
    by_exam = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        b = os.path.basename(p)
        if not re.match(r'(sol-|paper-)', b):
            continue
        t = text(p)
        eid = exam_of(b)
        for name, pat in CONST.items():
            for v in pat.findall(t):
                by_exam[eid][name][re.sub(r'\s+', '', v)] += 1

    bad = []
    print('회차 %d개에서 상수를 본다\n' % len(by_exam))
    for eid in sorted(by_exam):
        lines = []
        for name, c in sorted(by_exam[eid].items()):
            if len(c) > 1:
                lines.append('%s → %s' % (name, ' · '.join('%s(%d)' % kv for kv in c.most_common())))
        if lines:
            bad.append((eid, lines))
    if bad:
        print('한 회차 안에서 갈린 곳 %d회차' % len(bad))
        for eid, lines in bad:
            print('  [%s]' % eid)
            for t in lines:
                print('      ' + t)
    else:
        print('한 회차 안에서 갈린 곳 없음 — 문제지와 해설이 같은 값을 쓴다.')

    # ⚠ 지금 걸린 셋은 **어느 쪽이 맞는지 기계가 모른다.** 회차마다 시험지 표지에
    #   적힌 값이 다르고, 표지는 이 저장소에 글자로 안 들어와 있다. 어느 쪽으로
    #   맞출지는 그 시험지를 아는 사람이 정한다. 여기서는 **새로 생기는 것만** 막는다.
    if '--write' in sys.argv:
        json.dump({'설명': '선생님이 보고 남겨 둔 것. 여기 적힌 회차는 빨간불을 '
                           '안 켜고, 새로 생기는 것만 막는다. 어느 값으로 맞출지는 '
                           '그 회차 시험지 표지를 아는 사람이 정한다.',
                   '남겨 둔 회차': {eid: lines for eid, lines in bad}},
                  open(NOTE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n기록했다 · tools/const_sync.json')
        return 0
    known = {}
    if os.path.exists(NOTE):
        known = json.load(open(NOTE, encoding='utf-8')).get('남겨 둔 회차') or {}
    fresh = [(e, l) for e, l in bad if known.get(e) != l]
    if fresh:
        print('\n남겨 둔 것에 없는 새것 %d회차' % len(fresh))
        for e, _ in fresh:
            print('   ', e)
    if check:
        print('\n' + ('FAIL' if fresh else 'PASS'))
        return 1 if fresh else 0
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
