#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""틀린 문항에 **같은 개념의 동형문제**가 붙는지 회차마다 잰다.

왜 이 자가 있나
---------------
성적표 부록 「오답 정리 노트」는 틀린 문항마다 이렇게 적는다.

    왜 틀렸나 → 개념 보충 → ◈ 동형문제 · 같은 개념으로 새로 만든 문제

그 동형문제는 `retry-pool.json` 에서 **같은 유형(type)** 의 다른 문항을 데려와
`answers/<회차>.json` 의 줄기·보기·해설로 그린다. 그러니 붙으려면 두 가지가
동시에 있어야 한다 — 같은 type 을 가진 다른 문항이 있을 것, 그리고 그 문항이
줄기와 보기 넷을 갖고 있을 것.

2026-08-29 에 처음 재어 보니 **3,060문항 가운데 1,193개(39%)** 만 붙었다.
회차별로는 고르지 않고 극단으로 갈렸다.

    kch1to3 98% · kch1to2 95% · kch2final 90%      ← 단원평가는 잘 붙는다
    jmchc 여러 회차 10~30%
    usnco-2026-natl-1 2% · kmchc 심화 두 회차 0%   ← 사실상 안 붙는다

뿌리는 **type 표기가 917종으로 흩어진 것**이다. 같은 개념이 회차마다 다른
이름으로 적혀 있으면 아무리 같은 것을 물어도 서로를 못 찾는다. 표기를 모으면
이 수는 저절로 오른다 — 그래서 이 자는 **표기 통일의 성적표**이기도 하다.

⚠ 이 자는 «붙을 수 있는가» 만 본다. 붙은 문제가 **좋은 동형인지**는 안 본다 —
  그건 화학을 아는 사람이 본다. 재는 것과 검수하는 것은 다르다.

    python3 tools/twin_cover.py           # 회차별 커버리지
    python3 tools/twin_cover.py --check   # 커버리지가 **떨어지면** 빨간불
    python3 tools/twin_cover.py --seal    # 지금 값을 새 바닥으로 적는다
"""
import collections
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'twin_cover.json')

_ans = {}


def answers(eid):
    if eid not in _ans:
        p = os.path.join(ROOT, 'answers', '%s.json' % eid)
        _ans[eid] = (json.load(io.open(p, encoding='utf-8')).get('questions', {})
                     if os.path.exists(p) else {})
    return _ans[eid]


def usable(eid, q):
    """동형문제로 **그려질 수 있는가** — 줄기와 보기 넷이 있어야 한다."""
    d = answers(eid).get(str(q)) or {}
    return bool(str(d.get('stem') or '').strip()) and len(d.get('choices') or []) >= 4


def measure():
    pool = json.load(io.open(os.path.join(ROOT, 'retry-pool.json'), encoding='utf-8'))['q']
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    by_t = collections.defaultdict(list)
    by_a = collections.defaultdict(list)
    for x in pool:
        by_t[x['t']].append(x)
        by_a[x['a']].append(x)
    rows = []
    for e in xs:
        eid, nQ = e['id'], e['nQ']
        A, T = e.get('area') or [], e.get('type') or []
        same = area = none = 0
        for i in range(nQ):
            t = T[i] if i < len(T) else ''
            a = A[i] if i < len(A) else ''
            if any(not (c['e'] == eid and c['q'] == i + 1) and usable(c['e'], c['q'])
                   for c in by_t.get(t, [])):
                same += 1
            elif any(not (c['e'] == eid and c['q'] == i + 1) and usable(c['e'], c['q'])
                     for c in by_a.get(a, [])):
                area += 1
            else:
                none += 1
        rows.append({'id': eid, 'nQ': nQ, 'same': same, 'area': area, 'none': none})
    return rows


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    rows = measure()
    rows.sort(key=lambda r: r['same'] / r['nQ'])
    tq = sum(r['nQ'] for r in rows)
    ts = sum(r['same'] for r in rows)
    ta = sum(r['area'] for r in rows)
    tn = sum(r['none'] for r in rows)

    print('문항 %d · 같은 유형 동형이 붙는 것 %d (%d%%) · 영역만 %d · 아무것도 없음 %d'
          % (tq, ts, round(100 * ts / tq), ta, tn))
    print('\n%-24s %5s %14s %7s %7s' % ('회차', '문항', '같은 유형', '영역만', '없음'))
    for r in rows:
        print('%-24s %5d %8d(%3d%%) %7d %7d'
              % (r['id'], r['nQ'], r['same'], round(100 * r['same'] / r['nQ']),
                 r['area'], r['none']))

    now = {r['id']: r['same'] for r in rows}
    now['__total__'] = ts
    if seal:
        json.dump({'설명': '회차별로 동형문제가 붙는 문항 수. 이 수는 **늘기만 한다** — '
                           '줄면 빨간불이다. type 표기를 모으거나 answers 에 줄기·보기를 '
                           '채우면 저절로 오른다.',
                   '바닥': now},
                  io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/twin_cover.json 에 바닥으로 적었다.')
        return 0

    if not os.path.exists(SEAL):
        print('\n바닥이 없다 — python3 tools/twin_cover.py --seal 로 적어 둔다.')
        return 1 if check else 0

    was = json.load(io.open(SEAL, encoding='utf-8')).get('바닥', {})
    down = [(k, was[k], now.get(k, 0)) for k in sorted(was)
            if k != '__total__' and now.get(k, 0) < was[k]]
    up = [(k, was[k], now.get(k, 0)) for k in sorted(was)
          if k != '__total__' and now.get(k, 0) > was[k]]
    if up:
        print('\n늘었다 — 잘된 일이다 (%d회차):' % len(up))
        for k, a, b in up[:20]:
            print('  %-24s %d → %d' % (k, a, b))
        print('  python3 tools/twin_cover.py --seal 로 새 바닥을 적는다.')
    if down:
        print('\n**줄었다** %d회차 — 동형문제가 안 붙게 됐다:' % len(down))
        for k, a, b in down:
            print('  %-24s %d → %d' % (k, a, b))
        print('\ntype 이름을 바꿨거나 answers 의 줄기·보기가 사라졌다.')
        return 1 if check else 0
    if not up:
        print('\n동형문제가 붙는 문항이 줄지 않았다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
