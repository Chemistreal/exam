#!/usr/bin/env python3
"""시상 컷이 회차의 실제 난이도와 얼마나 맞는지 잰다.

성적표의 '수상(장려상 이상) 확률' 은 그 회차의 컷(`exams.json` 의 `cut`,
**오답 수** 기준)을 넘을 확률이다. 그런데 컷은 회차마다 똑같이 박혀 있고
난이도는 그렇지 않다. 기준 기록으로 재어 보면 이렇게 갈린다.

    jmchc-4    동상 이상 36%   (열한 명 중 넷)
    jmchc-11   동상 이상  0%   (열여섯 명 중 아무도)

같은 컷인데 어떤 회차는 셋에 하나가 받고 어떤 회차는 한 명도 못 받는다.
학생이 보는 확률은 그 회차가 얼마나 어려웠는지를 담지 못한다 — "수상 확률이
너무 낮게 나온다" 는 말의 뿌리가 여기에 있다.

**컷은 여기서 바꾸지 않는다.** 누구에게 무슨 상을 줄지는 가르치는 사람이
정하는 일이고, 기계가 회차마다 컷을 흔들면 지난 회차의 상과 뜻이 달라진다.
여기서는 **재어서 보여 줄 뿐**이다. 옮길지 말지는 선생님이 정한다.

기록이 적으면(기본 10명 미만) 비율이 사람 한 명에 크게 흔들리므로 세지 않는다.

    python3 tools/cut_fit.py              # 회차별로 실제 수상 비율을 보여 준다
    python3 tools/cut_fit.py --check      # 기록이 있는데 아무도 못 받는 회차를 알린다
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'cohort', 'baseline.json')
EXAMS = os.path.join(ROOT, 'exams.json')

MIN_N = 10          # 이보다 적으면 비율이 흔들려 세지 않는다
LABEL = ['', '대상', '금상', '은상', '동상']


def load():
    if not os.path.exists(BASE):
        return {}, {}
    base = json.load(open(BASE, encoding='utf-8')).get('exams') or {}
    data = json.load(open(EXAMS, encoding='utf-8'))
    rounds = data if isinstance(data, list) else data.get('exams', [])
    return base, {e['id']: e for e in rounds}


def rates(hist, nQ, cuts):
    """맞은 개수별 사람 수에서, 각 컷을 넘은 사람의 비율을 낸다."""
    n = sum(hist.values())
    out = []
    for c in cuts[1:]:
        need = nQ - c
        cnt = sum(v for k, v in hist.items() if k >= need)
        out.append(cnt / n if n else 0.0)
    return n, out


# 재어서 **선생님께 이미 알린** 회차. 컷을 옮길지는 가르치는 판단이라
# 자가 정하지 않는다(docs/선생님이-정할-칸.md 의 A9). 답을 주시기 전까지
# 이 회차는 빨간불이 아니라 «알고 있는 것» 으로 적힌다.
# ⚠ 여기 없는 회차가 새로 전원 미수상이 되면 그때는 그대로 빨간불이다 —
#   그것이 이 자를 두는 까닭이다.
KNOWN = {
    'jmchc-11': '16명 중 최고가 39/60(오답 21)이라 동상 컷(오답 18)에 못 닿았다. '
                '이웃 회차 최고는 오답 11~16 — 회차가 실제로 어려웠던 것이지 '
                '기록이 빠진 것이 아니다 (2026-09-05)',
}


def main():
    check = '--check' in sys.argv
    base, exams = load()
    if not base:
        print('기준 기록이 없다(cohort/baseline.json). 잴 것이 없다.')
        return 0

    print('컷은 회차마다 같다. 난이도는 그렇지 않다 — 실제로 몇 %가 받았는지 잰다.\n')
    print('%-16s %4s %-14s %s' % ('회차', '인원', '컷(오답)', '실제 수상 비율'))

    none_at_all = []
    seen = 0
    for eid in sorted(base):
        ex = exams.get(eid)
        if not ex:
            continue
        hist = {int(k): v for k, v in (base[eid].get('hist') or {}).items()}
        if not hist:
            continue
        n, rs = rates(hist, ex['nQ'], ex['cut'])
        if n < MIN_N:
            continue
        seen += 1
        cells = ' · '.join('%s %d%%' % (LABEL[i + 1], round(r * 100))
                           for i, r in enumerate(rs))
        print('%-16s %4d %-14s %s' % (eid, n, ','.join(map(str, ex['cut'])), cells))
        if rs and rs[-1] == 0:
            none_at_all.append((eid, n))

    if not seen:
        print('\n인원 %d명 이상인 회차가 없다.' % MIN_N)
        return 0

    fresh = [x for x in none_at_all if x[0] not in KNOWN]

    if none_at_all:
        print('\n기록이 있는데 **한 명도 상을 못 받은** 회차 %d개:' % len(none_at_all))
        for eid, n in none_at_all:
            mark = '' if eid in KNOWN else '   ← 새로 생겼다'
            print('    %-16s %d명 전원 미수상%s' % (eid, n, mark))
        print('\n그 회차를 본 학생에게는 수상 확률이 늘 바닥으로 나온다.')
        print('컷을 옮길지는 가르치는 판단이라 여기서 정하지 않는다 — 재어서 알릴 뿐이다.')
        for eid, _ in none_at_all:
            if eid in KNOWN:
                print('\n  %s — 이미 알린 것: %s' % (eid, KNOWN[eid]))
        if fresh:
            return 1 if check else 0
        return 0

    print('\n기록이 있는 회차는 모두 한 명 이상 상을 받았다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
