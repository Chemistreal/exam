#!/usr/bin/env python3
"""어려웠던 회차의 시상 기준을 조금 늦춰 준다 → `exams.json` 의 `cutAdj`

시상 컷은 회차마다 똑같이 박혀 있는데(오답 0·4·9·13·18) 난이도는 그렇지 않다.
기준 기록으로 재어 보면 같은 컷에서 동상 이상이 이렇게 갈린다.

    jmchc-4   36%  (열한 명 중 넷)
    jmchc-11   0%  (열여섯 명 전원 미수상)

11회를 본 학생은 아무리 잘 봐도 수상 확률이 바닥으로 나온다 — 그 학생이
못한 것이 아니라 그 회차가 어려웠던 것이다. 그래서 **어려운 회차만** 기준을
조금 늦춘다. 쉬운 회차는 건드리지 않는다(이미 준 상을 도로 가져오지 않는다).

세 가지를 지킨다.

  ① 목표에 맞춘다   지금 컷에서 동상 이상이 되는 비율의 **전 회차 중앙값**이
                    12% 다. 그보다 적게 나온 회차만, 12% 에 닿는 데 필요한
                    만큼을 후보로 잡는다.

  ② 천천히 움직인다  기록이 적으면 비율이 사람 한 명에 크게 흔들린다. 그래서
                    필요한 양을 다 주지 않고 w = N/(N+K) 만큼만 준다(K=30).
                    열 명이면 4분의 1, 마흔 명이면 절반 남짓이다. 기록이
                    쌓일수록 조금씩 더 다가간다 — 한 번에 뒤집지 않는다.

  ③ 조금만 늦춘다    아무리 어려워도 문항 수의 8%(60문항이면 5문항)를 넘지
                    않는다. 상의 뜻이 회차마다 달라지면 안 된다.

값은 여기서 미리 셈해 `exams.json` 에 `cutAdj` 로 적는다. 화면에서 그때그때
계산하지 않는 까닭은, 기준 기록이 늦게 도착하면 학생마다 다른 기준으로 상이
매겨질 수 있기 때문이다. 저장소에 박아 두면 누가 언제 열어도 같다.

    python3 tools/gen_cut_adj.py            # 어떻게 바뀌는지 보여 준다
    python3 tools/gen_cut_adj.py --write    # exams.json 에 적는다
    python3 tools/gen_cut_adj.py --check    # 적힌 값이 기록과 맞는지 (CI용)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'cohort', 'baseline.json')
EXAMS = os.path.join(ROOT, 'exams.json')

TARGET = 0.12     # 동상 이상이 되는 비율의 목표(지금 컷의 전 회차 중앙값)
K = 30            # 기록이 이만큼 쌓이면 필요한 양의 절반을 준다
CAP_RATIO = 0.08  # 아무리 어려워도 문항 수의 8% 까지
MIN_N = 8         # 이보다 적으면 흔들려서 안 건드린다
SLACK = 0.01      # 목표에 이미 닿은 회차가 경계에서 흔들리지 않게 두는 여유


def hist_values(h):
    out = []
    for k, c in (h or {}).items():
        out += [int(k)] * int(c)
    return sorted(out)


def rate_at(vals, nQ, cut):
    """오답 cut 개까지 봐주었을 때 그 안에 든 사람의 비율."""
    need = nQ - cut
    return sum(1 for x in vals if x >= need) / len(vals) if vals else 0.0


def compute():
    """회차마다 늦출 문항 수를 낸다. 기록이 없거나 얇으면 0."""
    base = {}
    if os.path.exists(BASE):
        base = json.load(open(BASE, encoding='utf-8')).get('exams') or {}
    data = json.load(open(EXAMS, encoding='utf-8'))
    rounds = data if isinstance(data, list) else data.get('exams', [])

    out = {}
    for ex in rounds:
        eid = ex['id']
        adj = 0
        detail = None
        b = base.get(eid)
        if b:
            vals = hist_values(b.get('hist'))
            n = len(vals)
            if n >= MIN_N:
                nQ, low = ex['nQ'], ex['cut'][-1]
                now = rate_at(vals, nQ, low)
                if now < TARGET - SLACK:
                    need = 0
                    while need < nQ and rate_at(vals, nQ, low + need) < TARGET:
                        need += 1
                    w = n / (n + K)
                    cap = round(nQ * CAP_RATIO)
                    adj = max(0, min(cap, round(need * w)))
                    detail = (n, now, need, cap, rate_at(vals, nQ, low + adj))
        out[eid] = (adj, detail)
    return rounds, out


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    rounds, calc = compute()

    print('어려웠던 회차만 시상 기준을 늦춘다 (목표 %d%% · K=%d · 상한 문항의 %d%%)\n'
          % (TARGET * 100, K, CAP_RATIO * 100))
    moved = drift = 0
    for ex in rounds:
        adj, d = calc[ex['id']]
        cur = int(ex.get('cutAdj') or 0)
        if adj != cur:
            drift += 1
        if adj:
            moved += 1
            n, now, need, cap, after = d
            print('  %-16s %3d명 · 지금 %2.0f%% → %2.0f%%   %d문항 늦춤 (필요 %d · 상한 %d)'
                  % (ex['id'], n, now * 100, after * 100, adj, need, cap))
    if not moved:
        print('  늦출 회차 없음')

    if not drift:
        print('\nexams.json 의 cutAdj 가 기록과 맞는다.')
        return 0

    if write:
        s = open(EXAMS, encoding='utf-8').read()
        data = json.loads(s)
        rs = data if isinstance(data, list) else data['exams']
        for ex in rs:
            adj = calc[ex['id']][0]
            if adj:
                ex['cutAdj'] = adj
            else:
                ex.pop('cutAdj', None)
        # 한 줄에 한 회차 — 이 파일이 지켜 온 꼴이다.
        body = ',\n'.join(json.dumps(e, ensure_ascii=False, separators=(',', ':'))
                          for e in rs)
        open(EXAMS, 'w', encoding='utf-8').write('[\n' + body + '\n]\n')
        print('\nexams.json 에 적었다 (%d개 회차 변경)' % drift)
        return 0

    print('\nexams.json 의 cutAdj 가 기록과 어긋난다 (%d개 회차).' % drift)
    print('python3 tools/gen_cut_adj.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    sys.exit(main())
