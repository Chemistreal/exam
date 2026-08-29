#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단원평가 아홉 회차의 **석차 모집단**을 index.html 안에서 되찾는다.

무슨 일이 있었나
----------------
`final.html` 은 석차·백분위를 `cohort/baseline.json` 의 `hist`(맞은 문항 수 →
사람 수)로 낸다. 그런데 단원평가 여덟 회차에는 `n` 과 `qc`(문항별 정답자 수)만
있고 **`hist` 가 없었다.** 그래서 학부모 성적표에 「연도누적 총석차」가 통째로
안 나왔다 — 응시자 1,523명이 실제로 저장소 안에 있는데도.

어디에 있었나. `index.html` 의 `SEEDS` 다. 회차마다 **학생 한 명이 한 줄**이고
그 줄은 영역별 점수다. 다 더하면 그 학생 총점이고, 문항당 3점이니 3으로 나누면
맞은 문항 수가 된다. 성적표 엑셀에서 뽑아 둔 것이라 새로 만드는 값이 아니라
**이미 저장소에 있던 것을 옮기는** 일이다.

    kch1to3 443 · kch1to3-b 418 · chem2-1 155 · kch1to2 145 ·
    kch1to2-b 145 · kch1u1 139 · kch2final 61 · kch2to3 17     = 1,523명

⚠ `j0`(조준모의고사 0회)은 **뺀다.** 그 회차 총점(BASE_TOTALS, 40명)에는
  3의 배수가 아닌 값이 11개 섞여 있다 — 문항당 3점으로 채점된 것이 아니라는
  뜻이다. 3으로 나누면 맞은 문항 수가 아닌 수가 나오고, 그 수로 석차를 매기면
  틀린 등수를 내보낸다. 모르는 것은 모른다고 둔다.

⚠ 이 자는 `qc` · `q` 를 **건드리지 않는다.** 그 둘은 성적표 엑셀에서 온 것이고
  (tools/gen_cohort_baseline.py), 여기서 채우는 것은 `hist` 한 칸뿐이다.

    python3 tools/gen_cohort_from_seeds.py           # 무엇이 채워지나
    python3 tools/gen_cohort_from_seeds.py --write   # baseline.json 에 적는다
    python3 tools/gen_cohort_from_seeds.py --check   # 있던 hist 가 사라지면 빨간불
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'index.html')
BASE = os.path.join(ROOT, 'cohort', 'baseline.json')
PT = 3


def seeds():
    s = io.open(IDX, encoding='utf-8').read()
    i = s.index('const SEEDS='); j = s.index('\n};', i) + 2
    return json.loads(s[i + len('const SEEDS='):j])


def hist_of(rows):
    """학생별 영역 점수 줄 → 맞은 문항 수 히스토그램. 안 나누어떨어지면 None."""
    tot = [sum(r) for r in rows]
    if any(t % PT for t in tot):
        return None, [t for t in tot if t % PT]
    h = {}
    for t in tot:
        k = str(t // PT)
        h[k] = h.get(k, 0) + 1
    return h, []


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    doc = json.load(io.open(BASE, encoding='utf-8'))
    ex = doc['exams']
    sd = seeds()

    add, keep, skip, lost = [], [], [], []
    for eid, rows in sorted(sd.items()):
        h, odd = hist_of(rows)
        if h is None:
            skip.append((eid, len(rows), len(odd)))
            continue
        cur = ex.get(eid)
        if cur is None:
            skip.append((eid, len(rows), -1))
            continue
        if cur.get('hist'):
            keep.append((eid, sum(cur['hist'].values())))
        else:
            add.append((eid, len(rows), min(int(k) for k in h), max(int(k) for k in h)))
            if write:
                cur['hist'] = h
                # 출처가 바뀌었다고 적는다. 'rate' 는 「정답률에서 세운 반쪽 기록 —
                # hist 가 없다」는 뜻이라, hist 를 넣고도 그대로 두면 그 이름이
                # 거짓말이 된다(tests/peer-rate.js 가 그것을 잡는다).
                if cur.get('from') == 'rate':
                    cur['from'] = 'rate+seeds'

    # 있던 것이 사라지지 않았나 — 이 자가 지키는 것은 그것이다
    for eid, e in ex.items():
        if eid in sd and not e.get('hist') and not any(a[0] == eid for a in add):
            lost.append(eid)

    print('SEEDS 회차 %d개 · baseline 회차 %d개' % (len(sd), len(ex)))
    if add:
        print('\nhist 를 채울 회차 %d개 (%d명):' % (add and len(add), sum(a[1] for a in add)))
        for eid, n, lo, hi in add:
            print('  %-12s %4d명 · 맞은 문항 %2d~%2d' % (eid, n, lo, hi))
    if keep:
        print('\n이미 hist 가 있는 회차 %d개: %s' % (len(keep), ', '.join(k[0] for k in keep)))
    if skip:
        print('\n안 채우는 회차 %d개:' % len(skip))
        for eid, n, odd in skip:
            print('  %-12s %s' % (eid, ('baseline 에 그 회차가 없다' if odd < 0 else
                  '총점 %d개가 %d의 배수가 아니다 — 문항당 %d점으로 채점된 것이 아니다' % (odd, PT, PT))))

    if write:
        io.open(BASE, 'w', encoding='utf-8').write(
            json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
        print('\ncohort/baseline.json 에 적었다.')
        return 0

    if lost:
        print('\n있던 hist 가 사라진 회차 %d개: %s' % (len(lost), ', '.join(lost)))
        return 1 if check else 0
    if add:
        print('\npython3 tools/gen_cohort_from_seeds.py --write 로 채운다.')
        return 1 if check else 0
    print('\n채울 것이 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
