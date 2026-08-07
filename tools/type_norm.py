#!/usr/bin/env python3
"""같은 말을 두 가지로 적고 있지 않은지 본다.

`네른스트 식` 과 `네른스트식` 은 사람에게는 같은 말이지만 기계에게는 다른
유형이다. 그러면 이런 일이 벌어진다.

  · 성적표의 유형 통계가 둘로 쪼개진다 — 다섯 문항 틀렸는데 셋과 둘로 나뉜다
  · OMLIB 에 줄을 하나 넣어 두고 나머지 하나가 빈 것을 모른다
  · 동형문제를 개념으로 모을 때 한쪽이 빠진다

띄어쓰기·가운뎃점·붙임표만 빼고 같아지면 같은 말로 본다. 어느 쪽으로 모을지는
기계가 정하지 않는다 — `헨더슨-하셀바흐식` 처럼 붙임표가 이름의 제 꼴인
경우가 있어서다. 여기서는 갈렸다는 것만 알린다.

    python3 tools/type_norm.py            # 갈린 것을 보여 준다
    python3 tools/type_norm.py --check    # 하나라도 갈렸으면 빨간불
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def key(s):
    """띄어쓰기·가운뎃점·붙임표를 지운 꼴."""
    return re.sub(r'[\s·\-]', '', s)


def collect():
    """(유형, 어디에 있는지) 를 모은다 — exams.json 의 type 과 answers 의 concept."""
    where = collections.defaultdict(collections.Counter)

    data = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    rounds = data if isinstance(data, list) else data.get('exams', [])
    for ex in rounds:
        for t in (ex.get('type') or []):
            if t:
                where[t]['exams.json'] += 1

    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        a = json.load(open(p, encoding='utf-8'))
        for q in (a.get('questions') or {}).values():
            c = (q.get('concept') or '').strip()
            if c:
                where[c][os.path.basename(p)] += 1
    return where


def main():
    check = '--check' in sys.argv
    where = collect()

    groups = collections.defaultdict(list)
    for t in where:
        groups[key(t)].append(t)
    split = {k: sorted(v) for k, v in groups.items() if len(v) > 1}

    print('유형 %d종' % len(where))
    if not split:
        print('띄어쓰기만 다른 짝: 없음')
        return 0

    print('\n같은 말인데 갈려 적힌 것 %d묶음:' % len(split))
    for k in sorted(split):
        print('  ' + ' / '.join(
            '%s (%d문항)' % (t, sum(where[t].values())) for t in split[k]))
        for t in split[k]:
            print('       %s  ←  %s' % (t, ', '.join(sorted(where[t]))))
    print('\n한쪽으로 모아라 — exams.json 의 type 과 answers 의 concept 을 함께 고친다.')
    print('어느 쪽이 맞는지는 사람이 정한다(붙임표가 이름의 제 꼴인 경우가 있다).')
    return 1 if check else 0


if __name__ == '__main__':
    sys.exit(main())
